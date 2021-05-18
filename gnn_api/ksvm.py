import pickle
from PIL import Image
from skimage.feature import hog
from skimage.color import rgb2gray
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import numpy as np
import os


class ksvmClassifier():

    def __init__(self, input_path):
        img = Image.open(input_path)
        self.data = np.asarray(img)
        root = os.getcwd()

        model_location = root + "/ksvm_model.sav"
        scalar_location = root + "/standardScalar.pkl"
        pca_location = root + "/pca.pkl"

        self.pca = pickle.load(open(pca_location, 'rb'))
        self.ss = pickle.load(open(scalar_location, 'rb'))
        self.ksvm = pickle.load(open(model_location, 'rb'))

    def feature_extraction(self, img):
        cf = img.flatten()
        gi = rgb2gray(img)
        hog_f = hog(gi, block_norm='L2-Hys', pixels_per_cell=(16, 16))
        flattened = np.hstack([cf, hog_f])
        flattened = np.array(flattened)
        return flattened

    def convert(self):
        features = self.feature_extraction(self.data)
        features = features.reshape(1, -1)
        f = self.ss.transform(features)
        reduced_f = self.pca.transform(features)
        return reduced_f

    def predict(self):
        reduced_f = self.convert()
        res = self.ksvm.predict_proba(reduced_f)
        return res.tolist()[0]
