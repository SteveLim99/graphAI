import jwt
import datetime
from dotenv import dotenv_values
config = dotenv_values("../env/jwt_secret.env")


def encode(cursor, user_id, SECRET_KEY):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=3600),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }

        potential_token = jwt.encode(
            payload,
            SECRET_KEY,
            algorithm='HS256'
        )

        while is_blacklist_token(cursor, potential_token)["status"]:
            potential_token = jwt.encode(
                payload,
                SECRET_KEY,
                algorithm='HS256'
            )

        return potential_token
    except Exception as e:
        return e


def decode(auth_token, SECRET_KEY):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(
            auth_token, SECRET_KEY, algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Token expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'


def check_if_exist(cursor, uid, uName, email):
    does_uid_exist = False
    does_user_exist = False
    does_email_exist = False

    if uid != None:
        statement = "select exists(select 1 from users where uid=%s limit 1)"
        cursor.execute(statement, (uid,))
        does_uid_exist = bool(cursor.fetchone()[0])

    if uName != None:
        statement = "select exists(select 1 from users where uname=%s limit 1)"
        cursor.execute(statement, (uName,))
        does_user_exist = bool(cursor.fetchone()[0])

    if email != None:
        statement = "select exists(select 1 from users where email=%s limit 1)"
        cursor.execute(statement, (email,))
        does_email_exist = bool(cursor.fetchone()[0])

    return does_user_exist or does_email_exist or does_uid_exist


def verify_token(token, cursor, SECRET_KEY):
    res = None
    if token:
        blacklisted_token_status = is_blacklist_token(cursor, token)
        blacklist_status, blacklist_msg = blacklisted_token_status[
            "status"], blacklisted_token_status["message"]

        if blacklist_status:
            res = {
                'status': blacklist_status,
                'message': blacklist_msg,
                'uid': None
            }

        else:
            uid = decode(token, SECRET_KEY)
            if not isinstance(uid, str):
                uid_exist = check_if_exist(cursor, uid, None, None)
                if uid_exist:
                    res = {
                        'status': True,
                        'message': 'User Verified.',
                        'uid': uid
                    }

                else:
                    res = {
                        'status': False,
                        'message': 'User Not Found.',
                        'uid': None
                    }
            else:
                res = {
                    'status': False,
                    'message': uid,
                    'uid': None
                }
    else:
        res = {
            'status': False,
            'message': 'Token Not Found.',
            'uid': None
        }
    return res


def is_blacklist_token(cursor, token):
    res = None
    msg = "Token Blacklisted."
    try:
        statement = "SELECT EXISTS (SELECT 1 FROM expired_tokens WHERE token = %s LIMIT 1)"
        cursor.execute(statement, (token,))
        blacklisted_token = bool(cursor.fetchone()[0])
        if not blacklisted_token:
            msg = "Token Verified."
        res = {
            'status': blacklisted_token,
            'message': msg
        }
    except (Exception, psycopg2.DatabaseError) as error:
        if conn:
            conn.rollback()
        res = {
            'status': True,
            'message': "An Error Occured. Please Re-try"
        }
    finally:
        if conn:
            conn.close()
        return res
