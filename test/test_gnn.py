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

# 1 - no token
def test_no_token(client):
    response = client.post("http://localhost:5001/gmlUpload?token=faketoken")
    response_body = json.loads(response.data)
    assert response_body["status"] == 'fail' and response_body["message"] == "Token Error: Invalid token, please log in again."

# 2 - no gcType
def test_no_token(client):
    response = client.post("http://localhost:5001/gmlUpload?token=" + token)
    response_body = json.loads(response.data)
    assert response_body["status"] == 'fail' and response_body["message"] == "Invalid parameter"

# 3 - no fname hash
def test_no_token(client):
    response = client.post("http://localhost:5001/gmlUpload?token=" + token + "&gcType=" + "ksvm")
    response_body = json.loads(response.data)
    assert response_body["status"] == 'fail' and response_body["message"] == "Invalid parameter"

# 4 - invalid fname hash
def test_no_token(client):
    response = client.post("http://localhost:5001/gmlUpload?token=" + token + "&gcType=" + "ksvm" + "&fname_hash=" + "jlsfkad")
    response_body = json.loads(response.data)
    assert response_body["status"] == 'fail' and response_body["message"] == "Invalid parameter"

# 5 - valid fname hash
def test_no_token(client):
    response = client.post("http://localhost:5001/gmlUpload?token=" + token + "&gcType=" + "ksvm" + "&fname_hash=" + "c5de9aaad16560271fd655dfede5cb841d74c100")
    response_body = json.loads(response.data)
    assert response_body["status"] == 'success' and response_body["message"] == "GNN Prediction Succesful"