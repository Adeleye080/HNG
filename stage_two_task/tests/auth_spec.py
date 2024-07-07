import pytest
import requests
import random, string


BASE_URL = 'http://127.0.0.1:5000'

characters = string.ascii_letters + string.digits
random_chars = ''.join(random.choice(characters) for _ in range(6))
    

@pytest.fixture(scope='module')
def user_data():
    return {
        'firstName': 'John',
        'lastName': 'Doe',
        'email': f'{random_chars}@example.com',
        'password': 'password123'
    }

@pytest.fixture(scope='module')
def auth_header(user_data):
    # Attempt to register the user
    response = requests.post(f'{BASE_URL}/auth/register', json=user_data)
    
    # If the user is already registered, log in
    if response.status_code == 422:
        response = requests.post(f'{BASE_URL}/auth/login', json={
            'email': user_data['email'],
            'password': user_data['password']
        })
    
    assert response.status_code == 200
    data = response.json()
    return {'Authorization': f'Bearer {data["data"]["accessToken"]}'}

def test_register_user(auth_header, user_data):
    response = requests.post(f'{BASE_URL}/auth/register', json=user_data)
    assert response.status_code == 422  # User already registered in auth_header

def test_login_user(user_data):
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'email': user_data['email'],
        'password': user_data['password']
    })
    assert response.status_code == 200
    data = response.json()
    assert 'accessToken' in data['data']

def test_get_user(auth_header, user_data):
    user_id = requests.post(f'{BASE_URL}/auth/login', json={
        'email': user_data['email'],
        'password': user_data['password']
    }).json()['data']['user']['userId']

    response = requests.get(f'{BASE_URL}/api/users/{user_id}', headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data['data']['user']['email'] == user_data['email']

def test_create_organization(auth_header):
    org_data = {
        "name": "Test Organization",
        "description": "This is a test organization."
    }
    response = requests.post(f'{BASE_URL}/api/organisations', json=org_data, headers=auth_header)
    assert response.status_code == 201
    data = response.json()
    
    assert data['data']['name'] == org_data['name']

def test_get_organizations(auth_header):
    response = requests.get(f'{BASE_URL}/api/organisations', headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data['data']['organisations'], list)

def test_get_organization_by_id(auth_header):
    org_id = requests.get(f'{BASE_URL}/api/organisations', headers=auth_header).json()['data']['organisations'][0]['orgId']
    response = requests.get(f'{BASE_URL}/api/organisations/{org_id}', headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data['data']['orgId'] == org_id

def test_add_user_to_organization(auth_header, user_data):
    org_id = requests.get(f'{BASE_URL}/api/organisations', headers=auth_header).json()['data']['organisations'][0]['orgId']
    user_id = requests.post(f'{BASE_URL}/auth/login', json={
        'email': user_data['email'],
        'password': user_data['password']
    }).json()['data']['user']['userId']

    response = requests.post(f'{BASE_URL}/api/organisations/{org_id}/users', json={'userId': user_id})
    assert response.status_code == 200 or 409 or 404
    data = response.json()
    if response.status_code == 200:
        assert data['message'] == 'User added to organisation successfully'
    elif response.status_code == 409:
        assert data['message'] == 'User already in organisation'
    elif response.status_code == 404:
        assert data['message'] == 'Organisation does not exist'


if __name__ == '__main__':
    pytest.main()
