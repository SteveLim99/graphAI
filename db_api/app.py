import psycopg2
from psycopg2.extensions import AsIs
from secrets import host, database, user, password
from flask import Flask, flash, request, redirect, url_for, send_file
import os
import io
from base64 import encodebytes
from PIL import Image
from data.graphs import graphs
from datetime import datetime
import sys

app = Flask(__name__)

UPLOAD_FOLDER = os.getcwd() + "/data/uploads/"
DOWNLOAD_FOLDER = os.getcwd() + "/data/predictions/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER


@app.route('/dbConnect',  methods=['GET', 'POST'])
def connectToDB():
    retries = 0
    max_retry = 5
    conn = None
    res = {}

    while retries != max_retry:
        try:
            processed = False
            conn = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password
            )

            cursor = conn.cursor()
            if request.method == 'POST':
                pred = request.args.get("pred")
                gid = graphs[pred]

                fName_file = open(app.config['UPLOAD_FOLDER'] +
                                  "file_name.txt", 'r')
                file_name = fName_file.readline()
                arrow = encode_img(app.config['DOWNLOAD_FOLDER'] +
                                   "detection_output_arrow.png")
                entity = encode_img(app.config['DOWNLOAD_FOLDER'] +
                                    "detection_output_entity.png")
                nx_img = encode_img(
                    app.config['DOWNLOAD_FOLDER'] + "networkx.png")

                date = datetime.today().strftime('%Y-%m-%d  %H:%M:%S')
                statement = "INSERT INTO files(name, input_date) VALUES(%s, TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS')) RETURNING id"
                cursor.execute(statement, (file_name, date, ))
                file_id = cursor.fetchone()[0]

                statement = "INSERT INTO images(id, arr, ent, nx) VALUES(%s, %s, %s, %s)"
                cursor.execute(statement, (file_id, arrow, entity, nx_img,))

                statement = "INSERT INTO prediction(id, gid) VALUES(%s, %s)"
                cursor.execute(statement, (file_id, gid,))

                statement = "INSERT INTO probability(id, gid, prob) VALUES(%s, %s, %s)"
                for key in graphs.keys():
                    probs = round(float(request.args.get(key)), 2)
                    gid = graphs[key]
                    cursor.execute(statement, (file_id, gid, probs,))

                tmp = readFiles()

                if tmp:
                    arr_file, ent_file, nx_file = tmp
                    arr_binary_data = psycopg2.Binary(arr_file)
                    ent_binary_data = psycopg2.Binary(ent_file)
                    nx_binary_data = psycopg2.Binary(nx_file)

                    statement = "INSERT INTO downloads(id, arr_file, ent_file, nx_file) VALUES (%s, %s, %s, %s)"
                    cursor.execute(
                        statement, (file_id, arr_binary_data, ent_binary_data, nx_binary_data, ))

                conn.commit()
                processed = True
                res = {"fileUploaded": str(processed), "graphID": str(file_id)}
                break

            elif request.method == 'GET':
                statement = "select * from getAll(keyword:=%s, start_year:=%s, end_year:=%s, graph_type:=%s)"

                keyword = None
                sYear = None
                eYear = None
                gType = None

                keyword = request.args.get("keyword")
                sYear = request.args.get("sDate")
                eYear = request.args.get("eDate")
                gType = request.args.get("gType")

                cursor.execute(statement, (keyword, sYear, eYear, gType))
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
                    db_probs = [str(i) for i in row[8]]

                    files_id.append(db_id)
                    files_name.append(db_name)
                    files_date.append(db_date)
                    files_gtype.append(db_gtype)
                    files_context.append(db_context)
                    files_probs.append(db_probs)

                    if db_arr != None:
                        file_img_arr.append(db_arr)
                    else:
                        file_img_arr.append("")

                    if db_ent != None:
                        file_img_ent.append(db_ent)
                    else:
                        file_img_ent.append("")

                    if db_nx != None:
                        file_img_nx.append(db_nx)
                    else:
                        file_img_nx.append("")

                res = {
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
    max_retry = 5
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
                    host=host,
                    database=database,
                    user=user,
                    password=password
                )
                cursor = conn.cursor()

                statement = "SELECT %s FROM downloads where id = %s"
                cursor.execute(statement, (AsIs(file), graph_id,))
                bdata = cursor.fetchone()[0]

                return send_file(
                    io.BytesIO(bdata),
                    as_attachment=True,
                    attachment_filename=filename
                )
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            retries += 1
            if conn:
                conn.rollback()
            print("Retry Attempt: " + str(retries) + " / " + str(max_retry))
    if conn:
        conn.close()
    return res


def encode_img(image_path):
    pil_img = Image.open(image_path, mode='r')  # reads the PIL image
    byte_arr = io.BytesIO()
    # convert the PIL image to byte array
    pil_img.save(byte_arr, format='PNG')
    encoded_img = encodebytes(byte_arr.getvalue()).decode(
        'ascii')  # encode as base64
    return encoded_img


def readFiles():
    arr_fin, ent_fin, nx_fin = None, None, None
    arr_file, ent_file, nx_file = None, None, None
    res = None

    try:
        arr_fin = open(
            (app.config['DOWNLOAD_FOLDER'] + "detection_output_arrow.png"), "rb")
        ent_fin = open(
            (app.config['DOWNLOAD_FOLDER'] + "detection_output_entity.png"), "rb")
        nx_fin = open(
            (app.config['DOWNLOAD_FOLDER'] + "network_obj.gml"), "rb")

        arr_file = arr_fin.read()
        ent_file = ent_fin.read()
        nx_file = nx_fin.read()

        res = [arr_file, ent_file, nx_file]
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
        return res
