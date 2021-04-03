import psycopg2
from secrets import host, database, user, password
from flask import Flask, flash, request, redirect, url_for, send_from_directory
import os
import io
from base64 import encodebytes
from PIL import Image
from data.graphs import graphs

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

                statement = "INSERT INTO files(name) VALUES(%s) RETURNING id"
                cursor.execute(statement, (file_name,))
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

                conn.commit()
                processed = True
                res = {"fileUploaded": str(processed)}
                break

            elif request.method == 'GET':
                statement = "select * from getAll()"
                cursor.execute(statement)
                rows = cursor.fetchall()

                files_id = []
                files_name = []
                file_img_arr = []
                file_img_ent = []
                file_img_nx = []
                files_gtype = []
                files_context = []
                files_probs = []
                for row in rows:
                    db_id = row[0]
                    db_name = row[1]
                    db_gtype = row[2]
                    db_context = row[3]
                    db_arr = row[4]
                    db_ent = row[5]
                    db_nx = row[6]
                    db_probs = [str(i) for i in row[7]]

                    files_id.append(db_id)
                    files_name.append(db_name)
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


def encode_img(image_path):
    pil_img = Image.open(image_path, mode='r')  # reads the PIL image
    byte_arr = io.BytesIO()
    # convert the PIL image to byte array
    pil_img.save(byte_arr, format='PNG')
    encoded_img = encodebytes(byte_arr.getvalue()).decode(
        'ascii')  # encode as base64
    return encoded_img
