from flask import Flask, flash, request, redirect, url_for
import os
from flask import jsonify
import torch
import dgl
import model
import networkx as nx
from dotenv import dotenv_values
from lib.utils.login import verify_token
import psycopg2

jwt_config = dotenv_values("./env/jwt_secret.env")
database_config = dotenv_values("./env/database.env")

app = Flask(__name__)
GML_MODEL = os.getcwd() + "/gcn_model"
app.config['GML_MODEL'] = GML_MODEL
NETWORK_FILE = os.getcwd() + "/data/predictions/network_obj.gml"
app.config['NETWORK_FILE'] = NETWORK_FILE
DOCUMENTATION_FILE = os.getcwd() + "/documentation/"
app.config['DOCUMENTATION_FILE'] = DOCUMENTATION_FILE


@app.route('/gmlUpload', methods=['POST'])
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

        if token_status:
            gnn_model = model.Classifier(1, 256, 2)

            gnn_model.load_state_dict(torch.load(app.config['GML_MODEL']))
            input_graph = nx.read_gml(app.config['NETWORK_FILE'])

            graph = dgl.from_networkx(input_graph)
            graph = dgl.add_self_loop(graph)

            res = gnn_model(graph)

            probs = torch.softmax(res, 1)
            sampled_Y = torch.multinomial(probs, 1)
            argmax_Y = torch.max(probs, 1)[1].view(-1, 1)

            np_probs = probs.detach().numpy()[0]
            int_res = argmax_Y.numpy()[0][0]

            str_res = "BPNM"
            if int_res == 1:
                str_res = "Swimlane"

            content = ""
            if str_res == "BPNM":
                with open(app.config['DOCUMENTATION_FILE'] + "bpnm.txt", "r") as f:
                    content = f.read()
            else:
                with open(app.config['DOCUMENTATION_FILE'] + "swimlane.txt", "r") as f:
                    content = f.read()

            res = {
                'prediction': str_res,
                'prob_0': str(np_probs[0]),
                'probs_1': str(np_probs[-1]),
                'content': content,
                'status': 'success',
                'message': 'GNN Prediction Succesful'
            }
        else:
            res = {
                'status': 'fail',
                'message': token_msg
            }
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        retries += 1
        res["message"] = error
        if conn:
            conn.rollback()
        print("Retry Attempt: " + str(retries) + " / " + str(max_retry))
    finally:
        if conn:
            conn.close()

    return jsonify(res)
