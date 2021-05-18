import os
import numpy as np
from PIL import Image
import inkmlToImg
import cv2
import matplotlib.pyplot as plt
import random
from xml.dom import minidom
import xml.etree.ElementTree as ET
import random
import math

class preProcessing:
    def reshape(self, img, x, y):
        return cv2.resize(img, dsize=(x, y), interpolation=cv2.INTER_CUBIC)

    def add_xml_objects(self, annotation, root):
        for elem in root:
                if elem.tag == "object":
                    obj = ET.SubElement(annotation, 'object')

                    for specs in elem:
                        if specs.tag == "bndbox":
                            bndbox = ET.SubElement(obj, 'bndbox')
                            for bbox in specs:
                                tag = bbox.tag
                                data = bbox.text
                                
                                new_tag = ET.SubElement(bndbox, tag)
                                new_tag.text = str(data)
                        else: 
                            tag = specs.tag
                            data = specs.text

                            new_tag = ET.SubElement(obj, tag)
                            new_tag.text = data

    def write_common_xml(self, path, file):
        annotation = ET.Element('annotation')

        folder = ET.SubElement(annotation, 'folder')
        folder.text = 'imgs'

        filename = ET.SubElement(annotation, 'filename')
        filename.text = file.split('.')[0] + ".png"

        filepath = ET.SubElement(annotation, 'filepath')
        filepath.text = path + file.split('.')[0] + ".png"

        source = ET.SubElement(annotation, 'source')
        database = ET.SubElement(source, 'database')
        database.text = 'Unknown'

        size = ET.SubElement(annotation, 'size')

        width = ET.SubElement(size, 'width')
        width.text = '800'

        height = ET.SubElement(size, 'height')
        height.text = '800'

        depth = ET.SubElement(size, 'depth')
        depth.text = '3'

        segmented = ET.SubElement(annotation, 'segmented')
        segmented.text = '0'

        return annotation

    def combine_xml(self, ARR_DIR, ENT_DIR, NEW_DIR, IMG_DIR):
        root = os.getcwd()
        arr_pth = root + ARR_DIR
        ent_pth = root + ENT_DIR
        new_pth = root + NEW_DIR
        labels = root + IMG_DIR

        arr = os.listdir(arr_pth)
        ent = os.listdir(ent_pth)

        for idx, (arr_file, ent_file) in enumerate(zip(arr, ent)):
            arr_doc = ET.parse(arr_pth + arr_file)
            ent_doc = ET.parse(ent_pth + ent_file)
            new_doc = open(new_pth + arr_file, 'wb')

            annotation = self.write_common_xml(labels, arr_file)
            arr_root = arr_doc.getroot()
            ent_root = ent_doc.getroot()
            self.add_xml_objects(annotation, arr_root)
            self.add_xml_objects(annotation, ent_root)

            new_doc_data = ET.tostring(annotation)
            new_doc.write(new_doc_data)

    def rotate_box(self, bb, cx, cy, h, w, theta):  
        new_bb = list(bb)                                                                                                                                                

        for i,coord in enumerate(bb):

            matrix = cv2.getRotationMatrix2D((cx, cy), theta, 1.0)

            cos = np.abs(matrix[0, 0])
            sin = np.abs(matrix[0, 1])                                   

            nW = int((h * sin) + (w * cos))
            nH = int((h * cos) + (w * sin))

            matrix[0, 2] += (nW / 2) - cx
            matrix[1, 2] += (nH / 2) - cy

            vector = [coord[0],coord[1],1]

            calculated = np.dot(matrix,vector)
            
            if theta == 90:
                if i == 0:
                    new_bb[i] = (math.floor(calculated[0]),math.ceil(calculated[1]))
                else:
                    new_bb[i] = (math.ceil(calculated[0]),math.floor(calculated[1]))
            elif theta == 180:
                if i == 0:
                    new_bb[i] = (math.ceil(calculated[0]),math.ceil(calculated[1]))
                else:
                    new_bb[i] = (math.floor(calculated[0]),math.floor(calculated[1]))
            else:
                if i == 0:
                    new_bb[i] = (math.ceil(calculated[0]),math.floor(calculated[1]))
                else:
                    new_bb[i] = (math.floor(calculated[0]),math.ceil(calculated[1]))

        xmin, ymin = new_bb[0]
        xmax, ymax = new_bb[1]
        if theta == 90:
            new_bb[0] = [xmin, ymax]
            new_bb[1] = [xmax, ymin]
        elif theta == 180:
            new_bb[0] = [xmax, ymax]
            new_bb[1] = [xmin, ymin]
        else: 
            new_bb[0] = [xmax, ymin]
            new_bb[1] = [xmin, ymax]
        return new_bb   

    def generate_rotated_xml(self, new_img_path, new_path, old_path, old_file, new_file, theta):
        doc = ET.parse(old_path + old_file)
        new_doc = open(new_path + new_file, 'wb')
        annotation = self.write_common_xml(new_img_path, new_file)

        doc_root = doc.getroot()
        for elem in doc_root:
                if elem.tag == "object":
                    obj = ET.SubElement(annotation, 'object')

                    for specs in elem:
                        if specs.tag == "bndbox":
                            bndbox = ET.SubElement(obj, 'bndbox')
                            bb = [0, 0, 0, 0]

                            for bbox in specs:
                                tag = bbox.tag
                                data = bbox.text

                                if tag == "xmin":
                                    bb[0] = int(data)
                                elif tag == "ymin":
                                    bb[1] = int(data)
                                elif tag == "xmax":
                                    bb[2] = int(data)
                                else: 
                                    bb[3] = int(data)
                            
                            old_bb = ((bb[0], bb[1]), (bb[2], bb[3]))
                            if theta != 0:
                                new_bb = self.rotate_box(old_bb, 400, 400, 800, 800, theta)
                            else: 
                                new_bb = old_bb

                            for idx, data in enumerate(new_bb):
                                x = data[0]
                                y = data[1]

                                if x < 0: x = 1
                                if x > 800: x = 799

                                if y < 0: y = 1
                                if y > 800: y = 799

                                if idx == 0:
                                    xmin_tag = ET.SubElement(bndbox, 'xmin')
                                    xmin_tag.text = str(x)
                                    
                                    ymin_tag = ET.SubElement(bndbox, 'ymin')
                                    ymin_tag.text = str(y)
                                elif idx == 1:
                                    xmax_tag = ET.SubElement(bndbox, 'xmax')
                                    xmax_tag.text = str(x)

                                    ymax_tag = ET.SubElement(bndbox, 'ymax')
                                    ymax_tag.text = str(y)
                        else: 
                            tag = specs.tag
                            data = specs.text

                            new_tag = ET.SubElement(obj, tag)
                            new_tag.text = data

        new_doc_data = ET.tostring(annotation)
        new_doc.write(new_doc_data)
                
    def gaussianNoise(self, img):
        upper_limit = random.uniform(1.0, 2.0)
        gauss = np.random.normal(0,upper_limit,img.size)
        gauss = gauss.reshape(img.shape[0],img.shape[1]).astype('uint8')
        img_gauss = cv2.add(img,gauss)
        return img_gauss


if __name__ == '__main__':
    preProcessing = preProcessing()

    root = os.getcwd()
    ARR_DIR = "/dataset/object_detection/data_augmentation/gn_labels/arrows/"
    ENT_DIR = "/dataset/object_detection/data_augmentation/gn_labels/entities/"
    NEW_DIR = "/dataset/object_detection/data_augmentation/gn_labels/combined/"
    IMG_DIR = "/dataset/object_detection/data_augmentation/gn_imgs/"

    img_new = root + "/dataset/object_detection/data_augmentation/rt_imgs/"
    arr_new = root + "/dataset/object_detection/data_augmentation/rt_labels/arrows/"
    ent_new = root + "/dataset/object_detection/data_augmentation/rt_labels/entities/"

    img_gb_new = root + "/dataset/object_detection/data_augmentation/gb_imgs/"
    arr_gb_new = root + "/dataset/object_detection/data_augmentation/gb_labels/arrows/"
    ent_gb_new = root + "/dataset/object_detection/data_augmentation/gb_labels/entities/"

    img_gn_new = root + "/dataset/object_detection/data_augmentation/gn_imgs/"
    arr_gn_new = root + "/dataset/object_detection/data_augmentation/gn_labels/arrows/"
    ent_gn_new = root + "/dataset/object_detection/data_augmentation/gn_labels/entities/"

    grey_img = root + "/dataset/object_detection/data_augmentation/grey_imgs/"

    preProcessing.combine_xml(ARR_DIR, ENT_DIR, NEW_DIR, IMG_DIR)

    imgs = os.listdir(root + IMG_DIR)
    arrs = os.listdir(root + ARR_DIR)
    ents = os.listdir(root + ENT_DIR)

    counter = 200
    gb_counter = 400
    gn_counter = 600

    for idx, (img, arr, ent) in enumerate(zip(imgs, arrs, ents)):
        new_img_file_name = "img_" + str(counter + idx) + ".png"
        new_anno_file_name = "img_" + str(counter + idx) + ".xml"

        new_img_gb_file_name = "img_" + str(gb_counter + idx) + ".png"
        new_anno_gb_file_name = "img_" + str(gb_counter + idx) + ".xml"

        new_img_gn_file_name = "img_" + str(gn_counter + idx) + ".png"
        new_anno_gn_file_name = "img_" + str(gn_counter + idx) + ".xml"
        
        img_path = root + IMG_DIR 
        arr_path = root + ARR_DIR 
        ent_path = root + ENT_DIR 

        img_curr = cv2.imread(img_path + img)
        img_curr = cv2.cvtColor(img_curr, cv2.COLOR_BGR2GRAY)

        ent_curr = ent_path + ent
        arr_curr = arr_path + arr

        rotated_idx = random.randint(0,2)
        blur_idx = random.randint(0,3)
        noise_idx = random.randint(0,3)
        rotated_img = None
        blurred_img = None
        noisy_img = None

        if rotated_idx == 0:
            rotated_img = cv2.rotate(img_curr, cv2.cv2.ROTATE_90_CLOCKWISE)
            preProcessing.generate_rotated_xml(img_new, arr_new, arr_path, arr, new_anno_file_name, 270)
            preProcessing.generate_rotated_xml(img_new, ent_new, ent_path, ent, new_anno_file_name, 270)
        elif rotated_idx == 1:
            rotated_img = cv2.rotate(img_curr, cv2.cv2.ROTATE_180)
            preProcessing.generate_rotated_xml(img_new, arr_new, arr_path, arr, new_anno_file_name, 180)
            preProcessing.generate_rotated_xml(img_new, ent_new, ent_path, ent, new_anno_file_name, 180)
        else:
            rotated_img = cv2.rotate(img_curr, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
            preProcessing.generate_rotated_xml(img_new, arr_new, arr_path, arr, new_anno_file_name, 90)
            preProcessing.generate_rotated_xml(img_new, ent_new, ent_path, ent, new_anno_file_name, 90)

        blur_rad_x = random.choice([5, 7, 9, 11, 13])
        blur_rad_y = random.choice([5, 7, 9, 11, 13])
        if blur_idx == 0:
            blurred_img = cv2.GaussianBlur(img_curr, (blur_rad_x, blur_rad_y), 0)
            preProcessing.generate_rotated_xml(img_gb_new, arr_gb_new, arr_path, arr, new_anno_gb_file_name, 0)
            preProcessing.generate_rotated_xml(img_gb_new, ent_gb_new, ent_path, ent, new_anno_gb_file_name, 0)
        elif blur_idx == 1:
            tmp = cv2.rotate(img_curr, cv2.cv2.ROTATE_90_CLOCKWISE)
            preProcessing.generate_rotated_xml(img_gb_new, arr_gb_new, arr_path, arr, new_anno_gb_file_name, 270)
            preProcessing.generate_rotated_xml(img_gb_new, ent_gb_new, ent_path, ent, new_anno_gb_file_name, 270)
            blurred_img = cv2.GaussianBlur(tmp, (blur_rad_x, blur_rad_y), 0)
        elif blur_idx == 2:
            tmp = cv2.rotate(img_curr, cv2.cv2.ROTATE_180)
            preProcessing.generate_rotated_xml(img_gb_new, arr_gb_new, arr_path, arr, new_anno_gb_file_name, 180)
            preProcessing.generate_rotated_xml(img_gb_new, ent_gb_new, ent_path, ent, new_anno_gb_file_name, 180)
            blurred_img = cv2.GaussianBlur(tmp, (blur_rad_x, blur_rad_y), 0)
        else:
            tmp = cv2.rotate(img_curr, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
            preProcessing.generate_rotated_xml(img_gb_new, arr_gb_new, arr_path, arr, new_anno_gb_file_name, 90)
            preProcessing.generate_rotated_xml(img_gb_new, ent_gb_new, ent_path, ent, new_anno_gb_file_name, 90)
            blurred_img = cv2.GaussianBlur(tmp, (blur_rad_x, blur_rad_y), 0)

        if noise_idx == 0:
            noisy_img = preProcessing.gaussianNoise(img_curr)
            preProcessing.generate_rotated_xml(img_gn_new, arr_gn_new, arr_path, arr, new_anno_gn_file_name, 0)
            preProcessing.generate_rotated_xml(img_gn_new, ent_gn_new, ent_path, ent, new_anno_gn_file_name, 0)
        if noise_idx == 1:
            tmp = cv2.rotate(img_curr, cv2.cv2.ROTATE_90_CLOCKWISE)
            preProcessing.generate_rotated_xml(img_gn_new, arr_gn_new, arr_path, arr, new_anno_gn_file_name, 270)
            preProcessing.generate_rotated_xml(img_gn_new, ent_gn_new, ent_path, ent, new_anno_gn_file_name, 270)
            noisy_img = preProcessing.gaussianNoise(tmp)
        elif noise_idx == 2:
            tmp = cv2.rotate(img_curr, cv2.cv2.ROTATE_180)
            preProcessing.generate_rotated_xml(img_gn_new, arr_gn_new, arr_path, arr, new_anno_gn_file_name, 180)
            preProcessing.generate_rotated_xml(img_gn_new, ent_gn_new, ent_path, ent, new_anno_gn_file_name, 180)
            noisy_img = preProcessing.gaussianNoise(tmp)
        else:
            tmp = cv2.rotate(img_curr, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
            preProcessing.generate_rotated_xml(img_gn_new, arr_gn_new, arr_path, arr, new_anno_gn_file_name, 90)
            preProcessing.generate_rotated_xml(img_gn_new, ent_gn_new, ent_path, ent, new_anno_gn_file_name, 90)
            noisy_img = preProcessing.gaussianNoise(tmp)
        
        cv2.imwrite(grey_img + img, img_curr)
        cv2.imwrite(img_new + new_img_file_name, rotated_img)
        cv2.imwrite(img_gb_new + new_img_gb_file_name, blurred_img)
        cv2.imwrite(img_gn_new + new_img_gn_file_name, noisy_img)