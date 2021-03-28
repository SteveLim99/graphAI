import networkx as nx
import csv
import pandas as pd
import matplotlib.pyplot as plt
import json
import os


class CsvToNetworkx():
    CSV_PATH = ""

    def __init__(self, CSV_PATH):
        super().__init__()
        self.CSV_PATH = CSV_PATH
        self.PD_ARROW_PATH = CSV_PATH + "detection_output_arrow.csv"
        self.PD_ENTITY_PATH = CSV_PATH + "detection_output_entity.csv"

    def intersection(self, xmin, ymin, xmax, ymax, node_xmin, node_ymin, node_xmax, node_ymax):
        # Calculate intersecting boundaries
        interLeft = max(xmin, node_xmin)
        interTop = max(ymin, node_ymin)
        interRight = min(xmax, node_xmax)
        interBottom = min(ymax, node_ymax)

        if interLeft < interRight and interTop < interBottom:
            return True
        return False

    def convert(self):
        pd_arrow, pd_entity = pd.read_csv(
            self.PD_ARROW_PATH), pd.read_csv(self.PD_ENTITY_PATH)
        G = nx.Graph()
        label_color_map = {
            'process': 'blue',
            'terminator': 'green',
            'decision': 'red'
        }

        all_edges = []
        entities = {}
        for index, row in pd_entity.iterrows():
            entity_class = row["class"]
            ymin, ymax = row["ymin"], row["ymax"]
            xmin, xmax = row["xmin"], row["xmax"]
            name = entity_class + "_" + str(index)
            G.add_node(
                name, color=label_color_map[entity_class], style='filled', fillcolor='blue')
            entities[name] = (ymin, xmin, ymax, xmax)

        for index, row in pd_arrow.iterrows():
            entity_class = row["class"]
            ymin, ymax = row["ymin"], row["ymax"]
            xmin, xmax = row["xmin"], row["xmax"]
            curr_edge = []
            for node in entities.keys():
                bbox = entities[node]
                node_ymin, node_ymax = bbox[0], bbox[2]
                node_xmin, node_xmax = bbox[1], bbox[3]
                found = False

                if self.intersection(xmin, ymin, xmax, ymax, node_xmin, node_ymin, node_xmax, node_ymax):
                    found = True

                if found:
                    if len(curr_edge) == 2:
                        sto_0, sto_1 = curr_edge[0], curr_edge[1]
                        all_edges.append(curr_edge)
                        all_edges.append([sto_0, node])
                        all_edges.append([sto_1, node])
                        curr_edge = []
                    else:
                        curr_edge.append(node)
            if(len(curr_edge) >= 2):
                all_edges.append(curr_edge)
        G.add_edges_from(all_edges)
        pos = nx.spring_layout(G)
        colored_dict = nx.get_node_attributes(G, 'color')
        default_color = 'blue'
        color_seq = [colored_dict.get(node, default_color)
                     for node in G.nodes()]

        root = os.getcwd()
        plt.ioff()
        fig = plt.figure()
        nx.draw(G, pos, with_labels=True, node_color=color_seq)
        plt.savefig(root + "/predictions/networkx.png")
        plt.close(fig)

        nx.write_gml(G, root + '/predictions/network_obj.gml')

        return G
