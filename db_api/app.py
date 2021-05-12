import psycopg2
from psycopg2.extensions import AsIs
from flask import Flask, flash, request, redirect, url_for, send_file
import os
import io
import base64 
from PIL import Image
from data.graphs import graphs
from datetime import datetime
from lib.utils.login import verify_token
from lib.utils.utils import deleteTemporaryFiles
import sys
from dotenv import dotenv_values

jwt_config = dotenv_values("./env/jwt_secret.env")
database_config = dotenv_values("./env/database.env")
app = Flask(__name__)

UPLOAD_FOLDER = os.getcwd() + "/data/uploads/"
DOWNLOAD_FOLDER = os.getcwd() + "/data/predictions/"
DB_MAX_RETRIES = 5
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['DB_MAX_RETRIES'] = DB_MAX_RETRIES


@app.route('/dbConnect',  methods=['GET', 'POST'])
def connectToDB():
    retries = 0
    max_retry = app.config['DB_MAX_RETRIES']
    conn = None
    res = {}

    while retries != max_retry:
        try:
            processed = False
            conn = psycopg2.connect(
                host=database_config["POSTGRES_HOST"],
                database=database_config["POSTGRES_DB"],
                user=database_config["POSTGRES_USER"],
                password=database_config["POSTGRES_PASSWORD"]
            )
            cursor = conn.cursor()
            token = request.args.get("token")
            token_verification = verify_token(
                token, cursor, jwt_config["SECRET_KEY"])
            token_status = token_verification["status"]
            token_msg = token_verification["message"]
            token_uid = token_verification["uid"]

            if token_status:
                if request.method == 'POST':

                    pred = request.args.get("pred")
                    ori_input_name = request.args.get("inputName")
                    fname_hash = request.args.get("fname_hash")

                    gid = graphs[pred]
                    file_name = ori_input_name
                    date = datetime.today().strftime('%Y-%m-%d  %H:%M:%S')
                    statement = "INSERT INTO predictions(name, input_date, uid) VALUES(%s, TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS'), %s, %s) RETURNING id"
                    cursor.execute(statement, (file_name, date, token_uid, gid,))
                    file_id = cursor.fetchone()[0]

                    statement = "INSERT INTO probability(id, gid, prob) VALUES(%s, %s, %s)"
                    for key in graphs.keys():
                        probs = round(float(request.args.get(key)), 2)
                        gid = graphs[key]
                        cursor.execute(statement, (file_id, gid, probs,))

                    tmp = readFiles(fname_hash)
                    if tmp:
                        arr_file, ent_file, nx_file, nx_png_file = tmp
                        arr_binary_data = psycopg2.Binary(arr_file)
                        ent_binary_data = psycopg2.Binary(ent_file)
                        nx_binary_data = psycopg2.Binary(nx_file)
                        nx_png_binary_data = psycopg2.Binary(nx_png_file)

                        statement = "INSERT INTO files(id, arr_file, ent_file, nx_file, nx_png_file) VALUES (%s, %s, %s, %s, %s)"
                        cursor.execute(
                            statement, (file_id, arr_binary_data, ent_binary_data, nx_binary_data, nx_png_binary_data,))

                    conn.commit()
                    processed = True
                    deleteTemporaryFiles(app.config['UPLOAD_FOLDER'], app.config['DOWNLOAD_FOLDER'], fname_hash)
                    res = {"fileUploaded": str(processed),
                           "graphID": str(file_id),
                           "status": "success",
                           "message": "Upload Succesful"}
                    break

                elif request.method == 'GET':
                    statement = "select * from getAll(keyword:=%s, start_year:=%s, end_year:=%s, graph_type:=%s, input_uid:=%s)"

                    keyword = None
                    sYear = None
                    eYear = None
                    gType = None

                    keyword = request.args.get("keyword")
                    sYear = request.args.get("sDate")
                    eYear = request.args.get("eDate")
                    gType = request.args.get("gType")

                    cursor.execute(statement, (keyword, sYear,
                                               eYear, gType, token_uid,))
                    rows = cursor.fetchall()

                    files_id = []
                    files_name = []
                    files_date = []
                    file_img_arr = []
                    file_img_ent = []
                    file_img_nx = []
                    files_gtype = []
                    files_context = []
                    files_probs = []
                    for row in rows:
                        db_id = row[0]
                        db_name = row[1]
                        db_date = row[2]
                        db_gtype = row[3]
                        db_context = row[4]

                        db_arr = row[5]
                        db_ent = row[6]
                        db_nx = row[7]

                        db_arr_bytes = base64.b64encode(db_arr)
                        db_ent_bytes = base64.b64encode(db_ent)
                        db_nx_bytes = base64.b64encode(db_nx)

                        db_arr_msg = db_arr_bytes.decode('ascii')
                        db_ent_msg = db_ent_bytes.decode('ascii')
                        db_nx_msg = db_nx_bytes.decode('ascii')

                        db_probs = [str(i) for i in row[8]]

                        files_id.append(db_id)
                        files_name.append(db_name)
                        files_date.append(db_date)
                        files_gtype.append(db_gtype)
                        files_context.append(db_context)
                        files_probs.append(db_probs)

                        if db_arr != None:
                            file_img_arr.append(db_arr_msg)
                        else:
                            file_img_arr.append("")

                        if db_ent != None:
                            file_img_ent.append(db_ent_msg)
                        else:
                            file_img_ent.append("")

                        if db_nx != None:
                            file_img_nx.append(db_nx_msg)
                        else:
                            file_img_nx.append("")

                    res = {
                        "status": "success",
                        "message": "Fetch Succesful",
                        "files_id": files_id,
                        "files_name": files_name,
                        "files_date": files_date,
                        "files_arr": file_img_arr,
                        "files_ent": file_img_ent,
                        "files_nx": file_img_nx,
                        "files_gtype": files_gtype,
                        "files_context": files_context,
                        "files_probs": files_probs
                    }
                    break
            else:
                res = {
                    "status": "fail",
                    "message": token_msg
                }
                break

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            retries += 1
            if conn:
                conn.rollback()
            print("Retry Attempt: " + str(retries) + " / " + str(max_retry))
    if conn:
        conn.close()
    return res


@app.route('/dbGetFile',  methods=['GET'])
def downloadFileFromDB():
    graph_id = request.args.get("id")
    file_type = request.args.get("file")

    retries = 0
    max_retry = app.config['DB_MAX_RETRIES']
    conn = None
    res = {}

    while retries != max_retry:
        try:
            if file_type == '0' or file_type == '1' or file_type == '2':
                file = ""
                filename = str(graph_id) + "_"
                if file_type == '0':
                    file = "arr_file"
                    filename += "arrow.png"
                if file_type == '1':
                    file = "ent_file"
                    filename += "entity.png"
                if file_type == '2':
                    file = "nx_file"
                    filename += "nx_obj.gml"

                conn = psycopg2.connect(
                    host=database_config["POSTGRES_HOST"],
                    database=database_config["POSTGRES_DB"],
                    user=database_config["POSTGRES_USER"],
                    password=database_config["POSTGRES_PASSWORD"]
                )
                cursor = conn.cursor()
                token = request.args.get("token")
                token_verification = verify_token(
                    token, cursor, jwt_config["SECRET_KEY"])
                token_status = token_verification["status"]
                token_msg = token_verification["message"]
                token_uid = token_verification["uid"]

                if token_status:
                    statement = "SELECT %s FROM downloads where id = %s"
                    cursor.execute(statement, (AsIs(file), graph_id,))
                    bdata = cursor.fetchone()[0]

                    return send_file(
                        io.BytesIO(bdata),
                        as_attachment=True,
                        attachment_filename=filename
                    )

                else:
                    res = {
                        'status': 'fail',
                        'message': token_msg
                    }
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            retries += 1
            if conn:
                conn.rollback()
            print("Retry Attempt: " + str(retries) + " / " + str(max_retry))
            res = {
                'status': 'fail',
                'message': error
            }
    if conn:
        conn.close()
    return res


@app.route('/dbDeleteFile', methods=['POST'])
def deleteFileFromDB():
    graph_id = request.args.get('id')

    retries = 0
    max_retry = app.config['DB_MAX_RETRIES']
    conn = None
    deleted = False
    res = None

    while retries != max_retry:
        try:
            print("Values currently being processed")
            input_id_int = int(graph_id)

            conn = psycopg2.connect(
                host=database_config["POSTGRES_HOST"],
                database=database_config["POSTGRES_DB"],
                user=database_config["POSTGRES_USER"],
                password=database_config["POSTGRES_PASSWORD"]
            )
            cursor = conn.cursor()
            token = request.args.get("token")
            token_verification = verify_token(
                token, cursor, jwt_config["SECRET_KEY"])
            token_status = token_verification["status"]
            token_msg = token_verification["message"]
            token_uid = token_verification["uid"]

            if token_status:
                statement = "SELECT * FROM delete_prediction(%s)"
                cursor.execute(statement, (input_id_int,))
                conn.commit()
                deleted = True
                res = {
                    'status': 'success',
                    'message': 'File Deleted'
                }

            else:
                res = {
                    'status': 'fail',
                    'message': token_msg
                }
            break
        except(Exception, psycopg2.DatabaseError, ValueError) as error:
            print(error)
            if type(error).__name__ == "ValueError":
                print("Value Provided is not of type Integer")
                break
            if conn:
                conn.rollback()
                print("Retry Attempt: " + str(retries) +
                      " / " + str(max_retry))
            res = {
                'status': 'fail',
                'message': error
            }
    if conn:
        conn.close()
    return res

def readFiles(fileName):
    arr_fin, ent_fin, nx_fin = None, None, None
    arr_file, ent_file, nx_file = None, None, None
    res = None

    try:
        arr_fin = open(
            (app.config['DOWNLOAD_FOLDER'] + fileName + "_arr.png"), "rb")
        ent_fin = open(
            (app.config['DOWNLOAD_FOLDER'] + fileName + "_ent.png"), "rb")
        nx_fin = open(
            (app.config['DOWNLOAD_FOLDER'] + fileName + "_nx.gml"), "rb")
        nx_png_fin = open(
            (app.config['DOWNLOAD_FOLDER'] + fileName + "_nx.png"), "rb")

        arr_file = arr_fin.read()
        ent_file = ent_fin.read()
        nx_file = nx_fin.read()
        nx_png_file = nx_png_fin.read()

        res = [arr_file, ent_file, nx_file, nx_png_file]
    except IOError as e:
        print(f'Error {e.args[0]}, {e.args[1]}')
        sys.exit(1)
    finally:
        if arr_fin:
            arr_fin.close()
        if ent_fin:
            ent_fin.close()
        if nx_fin:
            nx_fin.close()
        if nx_png_fin:
            nx_png_fin.close()
        return res