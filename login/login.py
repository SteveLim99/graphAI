import jwt
import datetime
from dotenv import dotenv_values
config = dotenv_values("../env/jwt_secret.env")


def encode(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            config["SECRET_KEY"],
            algorithm='HS256'
        )
    except Exception as e:
        return e


def decode(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(
            auth_token, config["SECRET_KEY"], algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'


if __name__ == "__main__":
    token = encode(1)
    print(token)
    decode = decode(token)
    print(decode)
