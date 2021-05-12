import pytest
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.utils.login import verify_token, check_if_exist, is_blacklist_token
import psycopg2
from dotenv import dotenv_values
import json
from app import app

jwt_config = dotenv_values("./env/jwt_secret.env")
database_config = dotenv_values("./env/database.env")
test_config = dotenv_values("./env/testing.env")

'''
 This file contains the automated unit test cases for the log in microservice
 ALL 10 test cases should pass,
 Code coverage is currently at 86% for endpoints and 82% for access managment code 
 Combined code coverage is at 84%

 Credentials utilized during testing are defined in testing.env
 WARNING: PLEASE DO NOT UTILIZE REAL USER ACCOUNT, PLEASE UTILIZE ACCOUNT CREATED FOR TESTING
 WARNING: PLEASE DO NOT PUSH CODE CONTAINING REAL USER CREDENTIALS TO GITHUB
'''
test_user = test_config["EXISTING_USER"]
test_email = test_config["EXISTING_EMAIL"]
test_pin = test_config["EXISTING_PIN"]
blacklisted_token_from_db = test_config["BLACKLIST_TOKEN"]

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# 1 - No token
def test_no_token():
    res = verify_token(None, None, None)
    assert res == {'status': False, 'message': 'Token Not Found.', 'uid': None}

# 2 - Test if user exist
def test_exist_user():
    conn = psycopg2.connect(
            host=database_config["POSTGRES_HOST"],
            database=database_config["POSTGRES_DB"],
            user=database_config["POSTGRES_USER"],
            password=database_config["POSTGRES_PASSWORD"]
        )
    cursor = conn.cursor()
    res = check_if_exist(cursor, 100, "lol", test_email)
    assert res == True

# 3 - Test a non blacklist token
def test_is_not_blacklist_token():
    conn = psycopg2.connect(
            host=database_config["POSTGRES_HOST"],
            database=database_config["POSTGRES_DB"],
            user=database_config["POSTGRES_USER"],
            password=database_config["POSTGRES_PASSWORD"]
        )
    cursor = conn.cursor()
    res = is_blacklist_token(cursor, "fake token")
    assert res == {
            'status': False,
            'message': "Token Verified."
        }

# 4 - Test a blacklisted token
def test_is_blacklist_token(client):
    response = client.post("http://localhost:5003/logout?token=" + blacklisted_token_from_db)
    response_body = json.loads(response.data)
    assert response_body["status"] == 'fail' and response_body["message"] == "Token Blacklisted."

# 5 - Test /registerUser - Existing user
def test_register_existing_user(client):
    response = client.post("http://localhost:5003/registerUser?uname=" + test_user + "&email=" + test_email + "&pw=" + test_pin)
    response_body = json.loads(response.data)
    assert response_body == {'auth_token': None, 'message': 'user name or email taken.', 'status': 'fail'}

# 6 - Test /login - Invalid PW
def test_invalid_pw(client):
    response = client.get("http://localhost:5003/login?uname=" + test_user + "&pw=fakepassword")
    response_body = json.loads(response.data)
    assert response_body == {
                    'status': 'fail',
                    'message': 'Incorrect Password.',
                    'auth_token': None
                }

# 7 - Test /login - Invalid user
def test_invalid_user(client):
    response = client.get("http://localhost:5003/login?uname=fakeuser&pw=fakepassword")
    response_body = json.loads(response.data)
    assert response_body == {
                    'status': 'fail',
                    'message': 'User does not exist.',
                    'auth_token': None
                }

# 8 - Test /login - Succesful user login
def test_valid_user(client):
    response = client.get("http://localhost:5003/login?uname=" + test_user + "&pw=" + test_pin)
    response_body = json.loads(response.data)
    assert response_body["status"] == "success" and response_body["message"] == "Logged in"

# 9 - Test /logout - Unsuccesful log out due to no token
def test_logout_no_token(client):
    response = client.post("http://localhost:5003/logout?token")
    response_body = json.loads(response.data)
    assert response_body["status"] == "fail" and response_body["message"] == "Token Not Found."

# 10 - Test /registerUser - Successful Registration
# 11 - Test /logout - Succesful Log out
# 10 and 11 were combined to utilize the token generated upon registration
# WARNING: PLEASE DELETE USER AFTER USAGE
def test_register_user(client):
    response_register = client.post("http://localhost:5003/registerUser?uname=unittest&email=unittest@gmail.com&pw=unittest")
    response_body_register = json.loads(response_register.data)
    mock_token_to_be_blacklisted = response_body_register["auth_token"]

    response_logout = client.post("http://localhost:5003/logout?token=" + str(mock_token_to_be_blacklisted))
    response_body_logout = json.loads(response_logout.data)

    assert response_body_register["status"] == "success" and response_body_register["message"] == "Successfully registered." and response_body_logout["message"] == "Logged Out." and response_body_logout["status"] == "success"
