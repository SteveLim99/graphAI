import pickle
from PIL import Image
from skimage.feature import hog
from skimage.color import rgb2grey
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import numpy as np

class ksvmClassifier():

    def __init__(self, input_path, model_location):
        img = Image.open(input_path)
        self.data = np.asarray(img)
        self.model_location = model_location

    def extract_features(self):
        color_features = img.flatten()
        grey_image = rgb2grey(img)
        hog_features = hog(grey_image, block_norm='L2-Hys', pixels_per_cell=(16, 16))
        flat_features = np.hstack([color_features, hog_features])
        return flat_features

    def convert(self):
        features = self.extract_features(self.data)
        ss = StandardScaler()
        f = ss.fit_transform(features)
        reduced_f = PCA(n_components=32)
        return reduced_f

    def predict(self):
        reduced_f = self.convert()
        ksvm = pickle.load(open(model_location, 'rb'))
        res = ksvm.predict(reduced_f)
        return res