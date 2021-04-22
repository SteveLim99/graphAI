from flask import Blueprint, request, make_response, jsonify
from flask import Flask, flash, redirect, url_for, send_file
from flask.views import MethodView
from login import encode, decode
from flask_bcrypt import Bcrypt
from dotenv import dotenv_values
from datetime import datetime
import psycopg2

app = Flask(__name__)
bcrypt = Bcrypt(app)

config = dotenv_values("../env/jwt_secret.env")


@app.route('/registerUser',  methods=['POST'])
def register_user():
    uName = request.args.get("uname")
    email = request.args.get("email")
    pw = request.args.get("pw")
    conn = None
    res = None
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="dev_postgres",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor()
        statement = "select exists(select 1 from users where uname=%s or email=%s limit 1)"
        cursor.execute(statement, (uName, email,))
        does_user_exist = bool(cursor.fetchone()[0])

        if not does_user_exist:
            pw_hash = bcrypt.generate_password_hash(pw)
            dt = datetime.today().strftime('%Y-%m-%d  %H:%M:%S')
            statement = "insert into users(uname, email, pw, register_date) values(%s, %s, %s, TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS')) RETURNING uid"
            cursor.execute(statement, (uName, email, pw_hash, dt,))
            uid = cursor.fetchone()[0]
            conn.commit()
            token = encode(uid)
            res = {
                'status': 'success',
                'message': 'Successfully registered.'
            }

        else:
            res = {
                'status': 'fail',
                'message': 'user name or email taken.'
            }
    except (Exception, psycopg2.DatabaseError) as error:
        print("error" + str(error))
        if conn:
            conn.rollback()
        res = {
            'status': 'fail',
            'message': 'Some error occurred. Please try again.'
        }
    finally:
        if conn:
            conn.close()
        return res
