from flask import Flask, flash, request, redirect, url_for
import os
from flask import jsonify
import torch
import dgl
import model
import networkx as nx

app = Flask(__name__)
GML_MODEL = os.getcwd() + "/gcn_model"
app.config['GML_MODEL'] = GML_MODEL
NETWORK_FILE = os.getcwd() + "/data/predictions/network_obj.gml"
app.config['NETWORK_FILE'] = NETWORK_FILE


@app.route('/gmlUpload', methods=['POST'])
def upload():
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

    return jsonify({'prediction': str_res, 'prob_0': str(np_probs[0]), 'probs_1': str(np_probs[-1])})
