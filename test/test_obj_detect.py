import pytest
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app
from dotenv import dotenv_values
import json
from io import BytesIO

jwt_config = dotenv_values("./env/jwt_secret.env")
database_config = dotenv_values("./env/database.env")
test_config = dotenv_values("./env/testing.env")

token = test_config["FAKE_TOKEN"]

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# 1 - no token
def test_no_token(client):
    response = client.post("http://localhost:5000/fileUpload?token=faketoken")
    response_body = json.loads(response.data)
    assert response_body["status"] == 'fail' and response_body["message"] == "Token Error: Invalid token, please log in again."

# 2 - no file
def test_no_file(client):
    response = client.post("http://localhost:5000/fileUpload?token=" + token)
    response_body = json.loads(response.data)
    assert response_body["status"] == 'fail' and response_body["message"] == "Missing File"

# 3 - no file name
def test_no_file_name(client):
    data = {
        'field': 'value',
        'file': (BytesIO(b'FILE CONTENT'), '')
        }
    response = client.post("http://localhost:5000/fileUpload?token=" + token,
                    content_type='multipart/form-data',
                    data=data   
    )
    response_body = json.loads(response.data)
    assert response_body["status"] == 'fail' and response_body["message"] == "No Selected File"

# 4 - wrong file extension
def test_wrong_file_extension(client):
    data = {
        'field': 'value',
        'file': (BytesIO(b'FILE CONTENT'), './test/test.txt')
        }
    response = client.post("http://localhost:5000/fileUpload?token=" + token,
                    content_type='multipart/form-data',
                    data=data   
    )
    response_body = json.loads(response.data)
    assert response_body["status"] == 'fail' and response_body["message"] == "Invalid File Extension."

# 5 - valid file for prediction
def test_valid_file(client):
    test_fin = open(('./test/fc_test.png'), "rb")
    test_file = test_fin.read()
    test_fin.close()

    data = {
        'field': 'value',
        'file': (BytesIO(test_file), './test/fc_test.png')
        }
    response = client.post("http://localhost:5000/fileUpload?token=" + token,
                    content_type='multipart/form-data',
                    data=data   
    )
    response_body = json.loads(response.data)
    assert response_body["status"] == 'success' and response_body["message"] == "RCNN Detection Succeeded."
