import psycopg2
from secrets import host, database, user, password
from flask import Flask, flash, request, redirect, url_for, send_from_directory
import os
import io
from base64 import encodebytes
from PIL import Image

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

                arrow = encode_img(app.config['DOWNLOAD_FOLDER'] +
                                   "detection_output_arrow.png")
                entity = encode_img(app.config['DOWNLOAD_FOLDER'] +
                                    "detection_output_entity.png")
                nx_img = encode_img(
                    app.config['DOWNLOAD_FOLDER'] + "networkx.png")

                statement = "INSERT INTO files(name,arrow,entity,nx_img) VALUES(%s, %s, %s, %s)"
                cursor.execute(
                    statement, ('test2', arrow, entity, nx_img,))
                conn.commit()
                processed = True
                res = {"fileUploaded": str(processed)}
                break

            elif request.method == 'GET':
                statement = "SELECT * FROM files"
                cursor.execute(statement)
                rows = cursor.fetchall()

                files = []
                file_img_arr = []
                file_img_ent = []
                file_img_nx = []
                for row in rows:
                    db_name = row[1]
                    db_arr = row[2]
                    db_ent = row[3]
                    db_nx = row[4]

                    files.append(db_name)
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
                    "files": files,
                    "files_arr": file_img_arr,
                    "files_ent": file_img_ent,
                    "files_nx": file_img_nx
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
