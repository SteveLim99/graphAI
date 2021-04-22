from flask import Blueprint, request, make_response, jsonify
from flask import Flask, flash, redirect, url_for, send_file
from flask.views import MethodView
from login import encode, decode
from flask_bcrypt import Bcrypt
from dotenv import dotenv_values
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
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="dev_postgres",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor()
        statement = "SELECT EXISTS(SELECT uid FROM users WHERE uname = %s)"
        cursor.execute(statement, (uName,))
        does_user_exist = cursor.fetchone()[0]
        print(does_user_exist)
        return str(does_user_exist)
    except (Exception, psycopg2.DatabaseError) as error:
        print("error" + str(error))
        if conn:
            conn.rollback()
        return "error"
    finally:
        if conn:
            conn.close()
