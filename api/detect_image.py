import visualization_utils as vis_util
import label_map_util
import csv_to_networkx
from matplotlib import pyplot as plt
from io import StringIO
from collections import defaultdict
import zipfile
import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow.compat.v1 as tf
import networkx as nx
import csv
import cv2
tf.disable_v2_behavior()

sys.path.append("..")


class ImageDetect():
    MODEL_NAME = ""
    PATH_TO_CKPT = ""
    PATH_TO_LABELS = ""
    NUM_CLASSES = ""
    EXPORT_PATH = ""
    IMAGE_PATH = ""
    IMAGE_SIZE = (12, 8)
    EXPORT_NAME = ""

    def __init__(self, MODEL_NAME, PATH_TO_CKPT, PATH_TO_LABELS, NUM_CLASSES, EXPORT_PATH, IMAGE_PATH, EXPORT_NAME):
        super().__init__()
        self.MODEL_NAME = MODEL_NAME
        self.PATH_TO_CKPT = PATH_TO_CKPT
        self.PATH_TO_LABELS = PATH_TO_LABELS
        self.NUM_CLASSES = NUM_CLASSES
        self.EXPORT_PATH = EXPORT_PATH
        self.IMAGE_PATH = IMAGE_PATH
        self.EXPORT_NAME = EXPORT_NAME

    def load_image_into_numpy_array(self, image):
        (im_width, im_height) = image.size
        return np.array(image.getdata()).reshape(
            (im_height, im_width, 3)).astype(np.uint8)

    def predict(self):
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        label_map = label_map_util.load_labelmap(self.PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(
            label_map, max_num_classes=self.NUM_CLASSES, use_display_name=True)
        category_index = label_map_util.create_category_index(categories)

        with detection_graph.as_default():
            with tf.Session(graph=detection_graph) as sess:
                with open(self.EXPORT_PATH + "/" + self.EXPORT_NAME + ".csv", "w") as out_file:
                    csv_writer = csv.writer(out_file)
                    image_path = self.IMAGE_PATH
                    # image = Image.open(image_path)
                    image = cv2.imread(image_path)
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    # the array based representation of the image will be used later in order to prepare the
                    # result image with boxes and labels on it.
                    image_ent = cv2.resize(image, dsize=(
                        800, 800), interpolation=cv2.INTER_CUBIC)
                    image_arr = cv2.resize(image, dsize=(
                        800, 800), interpolation=cv2.INTER_CUBIC)
                    # image_ent = load_image_into_numpy_array(image)
                    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                    image_ent_expanded = np.expand_dims(image_ent, axis=0)
                    image_tensor = detection_graph.get_tensor_by_name(
                        'image_tensor:0')
                    # Each box represents a part of the image where a particular object was detected.
                    boxes = detection_graph.get_tensor_by_name(
                        'detection_boxes:0')
                    # Each score represent how level of confidence for each of the objects.
                    # Score is shown on the result image, together with the class label.
                    scores = detection_graph.get_tensor_by_name(
                        'detection_scores:0')
                    classes = detection_graph.get_tensor_by_name(
                        'detection_classes:0')
                    num_detections = detection_graph.get_tensor_by_name(
                        'num_detections:0')
                    # Actual detection.
                    (boxes, scores, classes, num_detections) = sess.run(
                        [boxes, scores, classes, num_detections],
                        feed_dict={image_tensor: image_ent_expanded})
                    # Visualization of the results of a detection.

                    boxes, scores, classes = np.squeeze(
                        boxes), np.squeeze(scores), np.squeeze(classes).astype(np.int32)

                    ent_boxes, ent_scores, ent_classes = [], [], []
                    arr_boxes, arr_scores, arr_classes = [], [], []

                    for box, score, c in zip(boxes, scores, classes):
                        if c == 1:
                            arr_boxes.append(box)
                            arr_scores.append(score)
                            arr_classes.append(c)
                        else:
                            ent_boxes.append(box)
                            ent_scores.append(score)
                            ent_classes.append(c)

                    vis_util.visualize_boxes_and_labels_on_image_array(
                        image_ent,
                        np.array(ent_boxes),
                        np.array(ent_classes),
                        np.array(ent_scores),
                        category_index,
                        use_normalized_coordinates=True,
                        line_thickness=8)

                    vis_util.visualize_boxes_and_labels_on_image_array(
                        image_arr,
                        np.array(arr_boxes),
                        np.array(arr_classes),
                        np.array(arr_scores),
                        category_index,
                        use_normalized_coordinates=True,
                        line_thickness=8)

                    plt.figure(figsize=self.IMAGE_SIZE)
                    # matplotlib is configured for command line only so we save the outputs instead
                    plt.imshow(image_ent)
                    # create an outputs folder for the images to be saved
                    plt.savefig(
                        self.EXPORT_PATH + "/" + self.EXPORT_NAME + "_ent.png")

                    plt.imshow(image_arr)
                    plt.savefig(
                        self.EXPORT_PATH + "/" + self.EXPORT_NAME + "_arr.png"
                    )

                    height, width, _ = image_ent.shape
                    new_boxes = []
                    classes_list = np.squeeze(classes)
                    csv_writer.writerow(
                        ["class", "ymin", "xmin", "ymax", "xmax"])
                    for j, box in enumerate(boxes):
                        if(np.squeeze(scores)[j] > 0.5):
                            box[0] = box[0] * height
                            box[1] = box[1] * width
                            box[2] = box[2] * height
                            box[3] = box[3] * width
                            tmp = classes_list[j]
                            res = []
                            res.append(category_index[tmp]["name"])
                            res.append(box[0])
                            res.append(box[1])
                            res.append(box[2])
                            res.append(box[3])
                            new_boxes.append(res)
                            csv_writer.writerow(res)


if __name__ == "__main__":
    root = os.getcwd()
    imgd_entity = ImageDetect(
        MODEL_NAME="new_graph_rcnn",
        PATH_TO_CKPT=root + "/cbd_model/model/frozen_inference_graph.pb",
        PATH_TO_LABELS=root + "/cbd_model/object-detection.pbtxt",
        NUM_CLASSES=4,
        EXPORT_PATH=root + "/data/predictions/",
        IMAGE_PATH=root + "/data/uploads/" + "test.png",
        EXPORT_NAME="test"
    )
    imgd_entity.predict()
