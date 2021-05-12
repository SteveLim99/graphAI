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

test_user = test_config["EXISTING_USER"]
test_email = test_config["EXISTING_EMAIL"]
test_pin = test_config["EXISTING_PIN"]
blacklisted_token_from_db = test_config["BLACKLIST_TOKEN"]
expired_token = test_config["EXPIRED_TOKEN"]
fake_token = test_config["FAKE_TOKEN"]

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# 1 - Testing /dbGetFile - No params: id
def test_getFile_no_params(client):
    response = client.get("http://localhost:5002/dbGetFile")
    response_body = json.loads(response.data)
    assert response_body["status"] == 'fail' and response_body["message"] == "Missing Parameters"

# 2 - Testing /dbGetFile - Invalid file type
def test_getFile_invalid_file_type(client):
    response = client.get("http://localhost:5002/dbGetFile?token=" + blacklisted_token_from_db + "&file=50" + "&id=3")
    response_body = json.loads(response.data)
    assert response_body["status"] == 'fail' and response_body["message"] == "Invalid File Type."

# 3 - Testing /dbGetFile - Invalid token
def test_getFile_invalid_token(client):
    response = client.get("http://localhost:5002/dbGetFile?token=" + blacklisted_token_from_db + "&file=1" + "&id=3")
    response_body = json.loads(response.data)
    assert response_body["status"] == 'fail' and response_body["message"] == "Token Blacklisted."

# 4 - Testing /dbGetFile - File download
def test_getFile_valid_token(client):
    response = client.get("http://localhost:5002/dbGetFile?token=" + fake_token + "&file=1" + "&id=3")
    assert response.status_code == 200

# 5 - Testing /dbDeleteFile - No params: id
def test_dbDeleteFile_no_params(client):
    response = client.post("http://localhost:5002/dbDeleteFile")
    response_body = json.loads(response.data)
    assert response_body["status"] == 'fail' and response_body["message"] == "Missing Parameters"

# 6 - Testing /dbDeleteFile - Id is not integer
def test_dbDeleteFile_id_not_int(client):
    response = client.post("http://localhost:5002/dbDeleteFile?id=asd&token=" + fake_token)
    response_body = json.loads(response.data)
    assert response_body["status"] == 'fail' and response_body["message"] == "Value Provided is not of type Integer"

# 7 - Testing /dbDeleteFile - Invalid token
def test_dbDeleteFile_invalid_token(client):
    response = client.post("http://localhost:5002/dbDeleteFile?id=2&token=" + blacklisted_token_from_db)
    response_body = json.loads(response.data)
    assert response_body["status"] == 'fail' and response_body["message"] == "Token Blacklisted."

# 8 - Testing /dbConnect - Valid token
def test_dbConnect_get_valid_token(client):
    response = client.get("http://localhost:5002/dbConnect?token=" + fake_token)
    response_body = json.loads(response.data)
    assert response_body["status"] == 'success' and response_body["message"] == "Fetch Succesful"

# 9 - Testing /dbConnect - Invalid token
def test_dbConnect_get_invalid_token(client):
    response = client.get("http://localhost:5002/dbConnect?token=" + blacklisted_token_from_db)
    response_body = json.loads(response.data)
    assert response_body["status"] == 'fail' and response_body["message"] == "Token Blacklisted."

# 10 - Testing /dbConnect - Fetch random
def test_dbConnect_get_random_keyword(client):
    response = client.get("http://localhost:5002/dbConnect?token=" + fake_token + "&keyword=random")
    response_body = json.loads(response.data)
    assert response_body["status"] == 'success' and response_body["message"] == "Fetch Succesful"

# 11 - Testing /dbConnect - Saving inexistent file
def test_dbConnect_save_no_file(client):
    response = client.post("http://localhost:5002/dbConnect?token=" + \
                           fake_token + \
                           "&pred=BPNM" + \
                           "&inputName=fc_test.png" + \
                           "&fname_hash=c5de9aaad16560271fd655dfede5cb841d74c100" + \
                           "&Swimlane=0.4" + \
                           "&BPNM=0.6")
    response_body = json.loads(response.data)
    assert response_body["status"] == 'fail' and response_body["message"] == "File not present in file system."

# 12 - Testing /dbConnect - Saving file
def test_dbConnect_clean_save(client):
    response = client.post("http://localhost:5002/dbConnect?token=" + \
                           fake_token + \
                           "&pred=BPNM" + \
                           "&inputName=fc_test.png" + \
                           "&fname_hash=34c4a42e673da35c393f4c1b90ffba76bacaa0cb" + \
                           "&Swimlane=0.4" + \
                           "&BPNM=0.6")
    response_body = json.loads(response.data)
    assert response_body["status"] == 'success' and response_body["message"] == "Upload Succesful"

# 13 - Testing /dbDeleteFile - Deleting File
def test_dbDeleteFile_clean_delete(client):
    response = client.post("http://localhost:5002/dbDeleteFile?token=" + \
                          fake_token + \
                          "&id=8" )
    response_body = json.loads(response.data)
    assert response_body["status"] == 'success' and response_body["message"] == "File Deleted"