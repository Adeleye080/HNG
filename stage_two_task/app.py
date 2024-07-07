from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    JWTManager,
)
from models import User, Organization
from dotenv import load_dotenv
from os import getenv
from db import storage  # as st


load_dotenv()


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['JWT_SECRET_KEY'] = getenv('jwtSecretKey')
app.config['DEBUG'] = True
jwt = JWTManager(app)

# cross origin requesbt site
CORS(app, resources={r"/*": {"origins": "*"}},
     headers=['Content-Type', 'Authorization'],
     supports_credentials=True)


@app.before_request
def load_database_conn():
    # reload database
    storage.reload()


@app.teardown_appcontext
def close_database_conn(response):
    # close database connection
    storage.close()


@app.post('/auth/register')
def create_user():
    """create user endpoint."""
    # validate required inputs
    required_fields = ['firstName', 'lastName', 'email', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in request.json:
            missing_fields.append(field)

    if len(missing_fields) > 0:
        errors = [{'field': field, 'message': f'{field} is a required field'}
                  for field in missing_fields]
        return jsonify(errors=errors), 422

    firstName = request.json.get('firstName')
    lastName = request.json.get('lastName')
    email = request.json.get('email')
    password = request.json.get('password')
    phone = request.json.get('phone', None)

    # check if user already exists
    user_exist = storage.get_one(obj='User', filter={'email': email})
    # return 409 error if user already exist
    if user_exist:
        return jsonify({
            "status": "Conflict",
            "message": "User already exist",
            "statusCode": 422
        }), 422

    try:
        new_user = User(firstName=firstName, lastName=lastName,
                        email=email, password=password, phone=phone)
        new_org = Organization(name=f"{firstName}'s Organisation")
        # save user and org to database
        new_user.organizations.append(new_org)
        new_user.save()
        # new_org.save()
    except Exception as e:
        return jsonify({
            "status": "Bad request",
            "message": "Registration unsuccessful",
            "statusCode": 400
        }), 400

    access_token = create_access_token(identity=new_user.userId)

    response = {
        'status': 'success',
        "message": "Registration successful",
        'data': {
            'accessToken': access_token,
            'user': new_user.to_dict()
        }
    }

    return jsonify(response), 200


@app.post('/auth/login')
def log_in():
    email = request.json.get('email')
    password = request.json.get('password')

    required_fields = ['email', 'password']
    missing_fields = []

    for field in required_fields:
        if field not in request.json:
            missing_fields.append(field)

    if len(missing_fields) > 0:
        errors = [{'field': field, 'message': f'{field} is a required field'}
                  for field in missing_fields]
        return jsonify(errors=errors), 422

    # get user from database
    user = storage.get_one(obj='user', filter={"email": email})
    
    if not user:
        return jsonify(
            {
                "status": "Not found",
                "message": "User does not exist",
                "statusCode": 404
            }
        ), 404

    # check if user password match
    if not user.check_password(password):
        return jsonify(
            {
                "status": "Bad request",
                "message": "Authentication failed",
                "statusCode": 401
            }
        ), 401

    access_token = create_access_token(identity=user.userId)

    response = {
        'status': 'success',
        "message": "Login successful",
        'data': {
            'accessToken': access_token,
            'user': user.to_dict()
        }
    }

    return jsonify(response)


@app.get('/api/users/<string:id>')
@jwt_required()
def get_user(id):
    """
    Retrieve single user data
    """
    id_in_jwt = get_jwt_identity()

    # verify that client is owner of account
    if id_in_jwt != id:
        return jsonify(
            {
                "status": "Bad request",
                "message": "Authentication failed",
                "statusCode": 401
            }
        ), 401

    # retrieve user data
    user = storage.get_one(obj='user', filter={'userId': id})

    response = {
        'status': 'success',
        "message": "Request successful",
        'data': {
            'user': user.to_dict()
        }
    }

    return jsonify(response)


@app.get('/api/organisations')
@jwt_required()
def get_org_user_belong():
    """ Retrieves all organisation user belongs to """
    user_id = get_jwt_identity()

    # get user from database
    user = storage.get_one(obj='user', filter={'userId': user_id})
    if not user:
        return jsonify(
            {
                "status": "Bad request",
                "message": "User does not exist",
                "statusCode": 404
            }
        ), 404

    user_organizations = [org.to_dict() for org in user.organizations]

    response = {
        "status": "success",
        "message": "User organisation retrieval successful",
        "data": {
            "organisations": user_organizations
        }
    }

    return jsonify(response), 200


@app.get('/api/organisations/<string:orgId>')
@jwt_required()
def get_org_with_id(orgId):
    """ Get organisation with given Id """

    user_id = get_jwt_identity()

    org = storage.get_one(obj='org', filter={'orgId': orgId})
    if not org:
        return jsonify(
            {
                "status": "Bad request",
                "message": "Organisation does not exist",
                "statusCode": 404
            }
        ), 404

    user = storage.get_one(obj='user', filter={'userId': user_id})
    if not user:
        return jsonify(
            {
                "status": "Bad request",
                "message": "User does not exist",
                "statusCode": 404
            }
        ), 404

    if org not in user.organizations:
        return jsonify(
            {
                "status": "Forbidden",
                "message": "User is not authorized to view organisation",
                "statusCode": 403
            }
        ), 403

    response = {
        "status": "success",
        "message": "Retrieval successful",
        "data": org.to_dict()
    }

    return jsonify(response), 200


@app.post('/api/organisations')
@jwt_required()
def user_create_og():
    """ Endpoint for user to create their organisation """
    name = request.json.get('name')
    description = request.json.get('description', None)

    if 'name' not in request.json:
        return jsonify(
            {
                'errors': {
                    'field': 'name',
                    'message': 'namne field is a required field'
                }
            }
        ), 422

    # get user from database
    user_id = get_jwt_identity()
    user = storage.get_one(obj='user', filter={'userId': user_id})
    # create new org
    org = Organization(name=name, description=description)
    
    # add org to user's org collection
    user.organizations.append(org)
    user.save()
    
    org.name # this line loads the attrs, I dont know why its like that, its most likelya python 3.10.12 bug
    org = org.to_dict()

    return jsonify({
        "status": "success",
        "message": "Organisation created successfully",
        "data": org
    }), 201


@app.post('/api/organisations/<string:orgId>/users')
def add_user_to_org(orgId):
    """ add user to an organisation """
    user_id = request.json.get('userId')
    
    # verify that user id field is given
    if not user_id:
        return jsonify({'errors': [
            {'field': 'userId', 'message': 'userId is a required field'}
            ]}), 422

    # get org from database
    org = storage.get_one(obj='org', filter={'orgId': orgId})
    if not org:
        return jsonify(
            {
                "status": "Not found",
                "message": "Organisation does not exist",
                "statusCode": 404
            }
        ), 404
    
    user = storage.get_one(obj='user', filter={'userId': user_id})
    
    if org in user.organizations:
        return jsonify(
            {
                "status": "Conflict",
                "message": "User already in organisation",
                "statusCode": 409
            }
        ), 409
    
    user.organizations.append(org)
    user.save()
    
    return jsonify({
        "status": "success",
        "message": "User added to organisation successfully",
    }), 200


if __name__ == '__main__':
    app.run(port=5000)
