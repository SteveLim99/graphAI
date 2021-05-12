import os
import io
from base64 import encodebytes
from flask import jsonify
from PIL import Image
from flask import Flask, flash, request, redirect, url_for, send_from_directory
import detect_image
import csv_to_networkx
from lib.utils.login import verify_token
from lib.utils.utils import deleteTemporaryFiles
from dotenv import dotenv_values
import psycopg2
import hashlib
import datetime

jwt_config = dotenv_values("./env/jwt_secret.env")
database_config = dotenv_values("./env/database.env")

app = Flask(__name__)
UPLOAD_FOLDER = os.getcwd() + "/data/uploads/"
DOWNLOAD_FOLDER = os.getcwd() + "/data/predictions/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER


@app.route('/fileUpload', methods=['POST'])
def upload():
    conn = None
    res = {
        'status': 'fail',
        'message': ''
    }
    try:
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
        uid = token_verification["uid"]

        if token_status:
            if 'file' not in request.files:
                res["message"] = "Missing File"
            else:
                file = request.files['file']
                if file.filename == '':
                    res["message"] = "No Selected File"
                else:
                    if file and validateFileExtension(file.filename):
                        file_name_hash = generateFileNameHash(file.filename, uid)
                        file_name = file_name_hash + "_input.png"
                        root = os.getcwd()
                        
                        file.save(os.path.join(
                            app.config['UPLOAD_FOLDER'], file_name))

                        imgd_entity = detect_image.ImageDetect(
                            MODEL_NAME="new_graph_rcnn",
                            PATH_TO_CKPT=root + "/entity_model/new_graph_rcnn/frozen_inference_graph.pb",
                            PATH_TO_LABELS=root + "/entity_model/object-detection.pbtxt",
                            NUM_CLASSES=3,
                            EXPORT_PATH=app.config['DOWNLOAD_FOLDER'],
                            IMAGE_PATH=app.config['UPLOAD_FOLDER'] + file_name,
                            EXPORT_NAME=file_name_hash + "_ent"
                        )

                        imgd_arrow = detect_image.ImageDetect(
                            MODEL_NAME="new_graph_rcnn",
                            PATH_TO_CKPT=root + "/arrow_model/new_graph_arrow_rcnn/frozen_inference_graph.pb",
                            PATH_TO_LABELS=root + "/arrow_model/object-detection.pbtxt",
                            NUM_CLASSES=1,
                            EXPORT_PATH=app.config['DOWNLOAD_FOLDER'],
                            IMAGE_PATH=app.config['UPLOAD_FOLDER'] + file_name,
                            EXPORT_NAME=file_name_hash + "_arr"
                        )

                        imgd_arrow.predict()
                        imgd_entity.predict()

                        Conv_nx = csv_to_networkx.CsvToNetworkx(
                            CSV_PATH=app.config['DOWNLOAD_FOLDER'] + "/",
                            fileName=file_name_hash)
                        G = Conv_nx.convert()

                        prediction_path = app.config['DOWNLOAD_FOLDER'] + "/"
                        paths = os.listdir(prediction_path)
                        arrow_img = None
                        entity_img = None
                        networkx_img = None
                        for path in paths:
                            if(path.endswith("_arr.png")):
                                arrow_img = get_response_image(prediction_path + path)
                            elif(path.endswith("_ent.png")):
                                entity_img = get_response_image(prediction_path + path)
                            elif(path.endswith("_nx.png")):
                                networkx_img = get_response_image(
                                    prediction_path + path)
                        res = {
                            'arrow_img': arrow_img,
                            "entity_img": entity_img,
                            "networkx_img": networkx_img,
                            'file_name_hash': file_name_hash,
                            "status": "success",
                            "message": "RCNN Detection Succeeded."
                        }
                    else:
                        res["message"] = "Invalid File Extension."
        else:
            res["message"] = token_msg
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        res["message"] = error
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    return jsonify(res)


def get_response_image(image_path):
    pil_img = Image.open(image_path, mode='r')  # reads the PIL image
    byte_arr = io.BytesIO()
    # convert the PIL image to byte array
    pil_img.save(byte_arr, format='PNG')
    encoded_img = encodebytes(byte_arr.getvalue()).decode(
        'ascii')  # encode as base64
    return encoded_img


def validateFileExtension(fileExtension):
    return '.' in fileExtension and fileExtension.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generateFileNameHash(fileName, uid):
    file_name = fileName + \
        str(uid) + str(datetime.datetime.now())
    b_file_name = bytes(file_name, 'utf-8')
    hash_obj = hashlib.sha1(b_file_name)
    new_file_name = hash_obj.hexdigest()
    return new_file_name
