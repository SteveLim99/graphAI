import networkx as nx
import csv
import pandas as pd
import matplotlib.pyplot as plt
import json
import os


class CsvToNetworkx():
    CSV_PATH = ""

    def __init__(self, CSV_PATH, fileName):
        super().__init__()
        self.CSV_PATH = CSV_PATH + fileName + ".csv"
        self.fileName = fileName

    def get_cord_of_intersecting_rectangles(self, x_bbox, y_bbox):
        x_xmin, x_ymin, x_xmax, x_ymax = x_bbox
        y_xmin, y_ymin, y_xmax, y_ymax = y_bbox

        xmin   = max(x_xmin, y_xmin)
        ymin    = max(x_ymin, y_ymin)
        xmax  = min(x_xmax, y_xmax)
        ymax = min(x_ymax, y_ymax)
        
        return (xmin, ymin, xmax, ymax)

    def intersection(self, x_bbox, y_bbox):
        # Calculate intersecting boundaries
        xmin, ymin, xmax, ymax = self.get_cord_of_intersecting_rectangles(x_bbox, y_bbox)
        if xmin < xmax and ymin < ymax: 
            return True
        return False

    def get_potential_nodes(self, entities, arrow_bbox):
        potential_nodes = []
        for node in entities.keys():
            bbox = entities[node]
            node_ymin, node_ymax = bbox[0], bbox[2]
            node_xmin, node_xmax = bbox[1], bbox[3]

            if self.intersection(arrow_bbox, (node_xmin, node_ymin, node_xmax, node_ymax)):
                potential_nodes.append(node)
        return potential_nodes

    def get_iou_score(self, x_bbox, y_bbox):
        xmin, ymin, xmax, ymax = self.get_cord_of_intersecting_rectangles(x_bbox, y_bbox)
        intersection_area = (xmax - xmin) * (ymax - ymin)
        x_bbox_area = (x_bbox[2] - x_bbox[0]) * (x_bbox[3] - x_bbox[1])
        y_bbox_area = (y_bbox[2] - y_bbox[0]) * (y_bbox[3] - y_bbox[1])

        iou = intersection_area / float(x_bbox_area + y_bbox_area - intersection_area)
        return iou

    def evaluate_potential_nodes(self, entities, arrow_bbox, potential_nodes):
        total_nodes = len(potential_nodes)
        potential_edge = None
        if total_nodes == 2:
            potential_edge = potential_nodes
        elif total_nodes > 2:
            ious = []

            for i in potential_nodes:
                bbox = entities[i]
                node_ymin, node_ymax = bbox[0], bbox[2]
                node_xmin, node_xmax = bbox[1], bbox[3]

                iou = self.get_iou_score(
                    arrow_bbox, (node_xmin, node_ymin, node_xmax, node_ymax))
                ious.append((iou, i))

            ious = sorted(ious, key=lambda x: x[0], reverse=True)
            potential_edge = [x[-1] for x in ious[:2]]
        return potential_edge

    def convert(self):
        file = pd.read_csv(self.CSV_PATH)
        G = nx.Graph()
        label_color_map = {
            'process': 'blue',
            'terminator': 'green',
            'decision': 'red'
        }
        label_shape_map = {
            'process': '^',
            'terminator': 'o',
            'decision': 'd'
        }

        pd_arrow, pd_entity = [], []

        for index, row in file.iterrows():
            entity_class = row["class"]
            if entity_class == "arrow":
                pd_arrow.append((index, row))
            else:
                pd_entity.append((index, row))

        G = nx.Graph()
        entities = {}
        all_edges = []
        width = []
        height = []
        for index, row in pd_entity:
            entity_class = row["class"]
            ymin, ymax = row["ymin"], row["ymax"]
            xmin, xmax = row["xmin"], row["xmax"]
            width.append(xmax - xmin)
            height.append(ymax - ymin)
            name = entity_class + "_" + str(index)
            G.add_node(name, color=label_color_map[entity_class],
                       node_shape=label_shape_map[entity_class], style='filled', fillcolor='blue')
            entities[name] = (ymin, xmin, ymax, xmax)

        avg_width = sum(width) / len(width)
        avg_height = sum(height) / len(height)
        for index, row in pd_arrow:
            ymin, ymax = row["ymin"], row["ymax"]
            xmin, xmax = row["xmin"], row["xmax"]
            arrow_bbox = (xmin, ymin, xmax, ymax)

            potential_nodes = []
            potential_nodes = self.get_potential_nodes(entities, arrow_bbox)
            potential_edge = self.evaluate_potential_nodes(
                entities, arrow_bbox, potential_nodes)

            if potential_edge == None:
                potential_nodes = self.get_potential_nodes(
                    entities, (xmin-10, ymin-10, xmax+10, ymax+10))
                potential_edge = self.evaluate_potential_nodes(
                    entities, arrow_bbox, potential_nodes)

            if potential_edge and len(potential_edge) == 2 and potential_edge[::-1] not in all_edges and potential_edge not in all_edges:
                all_edges.append(potential_edge)

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
        plt.savefig(root + "/data/predictions/" + self.fileName + "_nx.png")
        plt.close(fig)

        nx.write_gml(G, root + '/data/predictions/' +
                     self.fileName + '_nx.gml')

        return G