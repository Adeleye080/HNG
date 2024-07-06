from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    JWTManager,
)
from models import User
from dotenv import load_dotenv
from os import getenv


load_dotenv()


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['JWT_SECRET_KEY'] = getenv('jwtSecretKey')
jwt = JWTManager(app)

# cross origin requesbt site
CORS(app, resources={r"/*": {"origins": "*"}},
     headers=['Content-Type', 'Authorization'],
     supports_credentials=True)


@app.before_request
def load_database_conn():
    # reload database
    pass


@app.teardown_appcontext
def close_database_conn(response):
    # close database connection
    pass


user = {
    "phone": "08129917445",
    "userId": "myID",
    "firstName": "Ajiboye",
    "lastName": "Pius",
    "email": "ajiboyeadeleye080@gmail.com",
    "password": "Testing123"
}


@app.post('/auth/register')
def create_user():
    """create user endpoint."""
    # validate required inputs
    required_fields = ['userId', 'firstName', 'lastName', 'email', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in request.json:
            missing_fields.append(field)

    if len(missing_fields) > 0:
        errors = [{'field': field, 'message': f'{field} is a required field'}
                  for field in missing_fields]
        return jsonify(errors=errors), 422

    userId = request.json.get('userId')
    firstName = request.json.get('firstName')
    lastName = request.json.get('lastName')
    email = request.json.get('email')
    password = request.json.get('password')
    phone = request.json.get('phone', None)

    try:
        new_user = User(userId=userId, firstName=firstName, lastName=lastName,
                        email=email, password=password, phone=phone)
        # new_user.save()
    except Exception:
        return jsonify({
            "status": "Bad request",
            "message": "Registration unsuccessful",
            "statusCode": 400
        }), 400

    access_token = create_access_token(identity=userId)

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

    new_user = User(**user)

    # check if user password match
    if password != new_user.password:  # dummy check for testing
        return jsonify(
            {
                "status": "Bad request",
                "message": "Authentication failed",
                "statusCode": 401
            }
        ), 401

    access_token = create_access_token(identity=new_user.userId)

    response = {
        'status': 'success',
        "message": "Login successful",
        'data': {
            'accessToken': access_token,
            'user': new_user.to_dict()
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

    # retrieve user data  DUMMY
    user = User(**user)  # represent data gotten from database!

    response = {
        'status': 'success',
        "message": "Login successful",
        'data': {
            'user': user.to_dict()
        }
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
