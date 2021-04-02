import psycopg2
from secrets import host, database, user, password
from flask import Flask, flash, request, redirect, url_for, send_from_directory

app = Flask(__name__)


@app.route('/dbConnect',  methods=['GET', 'POST'])
def connectToDB():
    if request.method == 'POST':
        retries = 0
        max_retry = 5
        db_version = ""
        while retries != max_retry:
            try:
                conn = psycopg2.connect(
                    host=host,
                    database=database,
                    user=user,
                    password=password
                )
                cursor = conn.cursor()
                statement = "SELECT version()"
                cursor.execute(statement)
                db_version = cursor.fetchone()
                cursor.close()
                break
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                retries += 1
                print("Retry Attempt: " + str(retries) + " / " + str(max_retry))
        return {"hello": str(db_version)}
    elif request.method == 'GET':
        return {"hello": "GET"}
