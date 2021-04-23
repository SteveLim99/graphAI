from flask import Blueprint, request, make_response, jsonify
from flask import Flask, flash, redirect, url_for, send_file
from flask.views import MethodView
from login import encode, decode, check_if_exist, verify_token
from flask_bcrypt import Bcrypt
from dotenv import dotenv_values
from datetime import datetime
import psycopg2

app = Flask(__name__)
bcrypt = Bcrypt(app)

jwt_config = dotenv_values("./env/jwt_secret.env")
database_config = dotenv_values("./env/database.env")


@app.route('/registerUser',  methods=['POST'])
def register_user():
    uName = request.args.get("uname")
    email = request.args.get("email")
    pw = request.args.get("pw")
    conn = None
    res = None
    try:
        conn = psycopg2.connect(
            host=database_config["POSTGRES_HOST"],
            database=database_config["POSTGRES_DB"],
            user=database_config["POSTGRES_USER"],
            password=database_config["POSTGRES_PASSWORD"]
        )
        cursor = conn.cursor()
        does_user_exist = check_if_exist(cursor, None, uName, email)

        if not does_user_exist:
            pw_hash = bcrypt.generate_password_hash(pw).decode()
            dt = datetime.today().strftime('%Y-%m-%d  %H:%M:%S')
            statement = "insert into users(uname, email, pw, register_date) values(%s, %s, %s, TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS')) RETURNING uid"
            cursor.execute(statement, (uName, email, pw_hash, dt,))
            uid = cursor.fetchone()[0]
            conn.commit()
            token = encode(uid, jwt_config["SECRET_KEY"])
            res = {
                'status': 'success',
                'message': 'Successfully registered.',
                'auth_token': token
            }

        else:
            res = {
                'status': 'fail',
                'message': 'user name or email taken.'
            }
    except (Exception, psycopg2.DatabaseError) as error:
        if conn:
            conn.rollback()
        res = {
            'status': 'fail',
            'message': 'Some error occurred. Please try again.'
        }
    finally:
        if conn:
            conn.close()
        return make_response(res)


@app.route('/login',  methods=['GET'])
def login_user():
    uName = request.args.get("uname")
    pw = request.args.get("pw")
    conn = None
    res = None

    try:
        conn = psycopg2.connect(
            host=database_config["POSTGRES_HOST"],
            database=database_config["POSTGRES_DB"],
            user=database_config["POSTGRES_USER"],
            password=database_config["POSTGRES_PASSWORD"]
        )
        cursor = conn.cursor()
        does_user_exist = check_if_exist(cursor, None, uName, None)

        if does_user_exist:
            statement = "select uid, pw from users where uname=%s"
            cursor.execute(statement, (uName,))
            cred = list(cursor.fetchone())
            uid, db_pw = cred[0], cred[1].encode('utf-8')
            is_pw_true = bcrypt.check_password_hash(db_pw, pw)

            if is_pw_true:
                token = encode(uid, jwt_config["SECRET_KEY"])
                res = {
                    'status': 'success',
                    'message': 'Logged in',
                    'auth_token': token
                }

            else:
                res = {
                    'status': 'fail',
                    'message': 'Incorrect Password.'
                }
        else:
            res = {
                'status': 'fail',
                'message': 'User does not exist.'
            }
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        if conn:
            conn.rollback()
        res = {
            'status': 'fail',
            'message': 'Some error occurred. Please try again.'
        }
    finally:
        if conn:
            conn.close()
        return make_response(res)


@app.route('/logout',  methods=['POST'])
def check_user_status():
    token = request.args.get("token")
    conn = None
    res = None

    try:
        conn = psycopg2.connect(
            host=database_config["POSTGRES_HOST"],
            database=database_config["POSTGRES_DB"],
            user=database_config["POSTGRES_USER"],
            password=database_config["POSTGRES_PASSWORD"]
        )
        cursor = conn.cursor()

        token_verification_res = verify_token(
            token, cursor, jwt_config["SECRET_KEY"])
        status, msg, uid = token_verification_res["status"], token_verification_res[
            "message"], token_verification_res["uid"]

        if status:
            dt = datetime.today().strftime('%Y-%m-%d  %H:%M:%S')
            statement = "INSERT INTO expired_tokens(uid, token, expiry_date) VALUES(%s, %s, TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS'))"
            cursor.execute(statement, (uid, token, dt))
            conn.commit()
            res = {
                'status': 'success',
                'message': 'Logged Out.'
            }
        else:
            res = {
                'status': 'fail',
                'message': msg
            }
    except (Exception, psycopg2.DatabaseError) as error:
        if conn:
            conn.rollback()
        res = {
            'status': 'fail',
            'message': 'Some error occurred. Please try again.'
        }
    finally:
        if conn:
            conn.close()
        return make_response(res)
