import os
import io
from base64 import encodebytes
from flask import jsonify
from PIL import Image
from flask import Flask, flash, request, redirect, url_for, send_from_directory
import detect_image
import csv_to_networkx

app = Flask(__name__)
UPLOAD_FOLDER = os.getcwd() + "/uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/test')
def test():
    return "Hello React"


@app.route('/fileUpload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "Missing File"
        file = request.files['file']
        if file.filename == '':
            return "No Selected File"
        if file and validateFileExtension(file.filename):
            file.save(os.path.join(
                app.config['UPLOAD_FOLDER'], "input_file.png"))
            root = os.getcwd()

            imgd_entity = detect_image.ImageDetect(
                MODEL_NAME="new_graph_rcnn",
                PATH_TO_CKPT=root + "/entity_model/new_graph_rcnn/frozen_inference_graph.pb",
                PATH_TO_LABELS=root + "/entity_model/object-detection.pbtxt",
                NUM_CLASSES=3,
                EXPORT_PATH=root + "/predictions",
                IMAGE_PATH=root + "/uploads/" + "input_file.png",
                EXPORT_NAME="detection_output_entity"
            )

            imgd_arrow = detect_image.ImageDetect(
                MODEL_NAME="new_graph_rcnn",
                PATH_TO_CKPT=root + "/arrow_model/new_graph_arrow_rcnn/frozen_inference_graph.pb",
                PATH_TO_LABELS=root + "/arrow_model/object-detection.pbtxt",
                NUM_CLASSES=1,
                EXPORT_PATH=root + "/predictions",
                IMAGE_PATH=root + "/uploads/" + "input_file.png",
                EXPORT_NAME="detection_output_arrow"
            )

            imgd_arrow.predict()
            imgd_entity.predict()

            Conv_nx = csv_to_networkx.CsvToNetworkx(
                CSV_PATH=root + "/predictions/")
            G = Conv_nx.convert()

            prediction_path = root + "/predictions/"
            paths = os.listdir(prediction_path)
            arrow_img = None
            entity_img = None
            networkx_img = None
            for path in paths:
                if(path.endswith("arrow.png")):
                    arrow_img = get_response_image(prediction_path + path)
                elif(path.endswith("entity.png")):
                    entity_img = get_response_image(prediction_path + path)
                elif(path.endswith("networkx.png")):
                    networkx_img = get_response_image(prediction_path + path)
            return jsonify({'arrow_img': arrow_img, "entity_img": entity_img, "networkx_img": networkx_img})


@app.route('/fileDownload', methods=['POST'])
def download():
    FILEPATH = os.getcwd() + "/predictions/"
    FILENAME = ""
    id = request.args.get("id")
    if id == '0':
        FILENAME = "detection_output_entity.png"
    elif id == '1':
        FILENAME = "detection_output_arrow.png"
    elif id == '2':
        FILENAME = "network_obj.gml"
    else:
        return
    return send_from_directory(directory=FILEPATH, filename=FILENAME)


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
