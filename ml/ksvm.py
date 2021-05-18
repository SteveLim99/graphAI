from google.colab import drive
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.optimize import minimize
from PIL import Image
from skimage.feature import hog
from skimage.color import rgb2grey
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.svm import SVC
import pandas as pd
from sklearn.metrics import accuracy_score
import pickle
import random

"""## Utility Functions

"""
# Code for Confusion Matrix Plot


def get_tp(test, pred):
    res = (test == 1)
    tp = (test[res] == pred[res]).sum()
    return tp.item()


def get_tn(test, pred):
    res = (test == 0) | (test == -1)
    tn = (test[res] == pred[res]).sum()
    return tn.item()


def get_fn(test, pred):
    res = (pred == 0) | (pred == -1)
    tn = (test[res] != pred[res]).sum()
    return tn.item()


def get_fp(test, pred):
    res = (pred == 1)
    tn = (test[res] != pred[res]).sum()
    return tn.item()


def plot_confusion_matrix(test, pred):
    tp = get_tp(test, pred)
    tn = get_tn(test, pred)
    fp = get_fp(test, pred)
    fn = get_fn(test, pred)

    cf = np.array([[tn, fn], [fp, tp]])
    fig, ax = plt.subplots()
    f1 = tp / (tp + 0.5 * (fp + fn))
    ax.matshow(cf, cmap=plt.cm.Blues)
    for i in range(2):
        for j in range(2):
            c = cf[j, i]
            ax.text(i, j, str(c), va='center', ha='center')
    print("F1 Score : " + str(f1))
    plt.xlabel('Prediction')
    plt.ylabel('Target')
    plt.show()


"""## Dataset Loading

"""

# Commented out IPython magic to ensure Python compatibility.
drive.mount('/content/gdrive')

# change to working tensorflow directory on the drive
# %cd '/content/gdrive/My Drive/TF/models'

BPNM_TRAIN = "/content/gdrive/My Drive/TF/models/research/object_detection/dataset/ds_gc/bpnm_train/"
BPNM_TEST = "/content/gdrive/My Drive/TF/models/research/object_detection/dataset/ds_gc/bpnm_test/"
SWIM_TRAIN = "/content/gdrive/My Drive/TF/models/research/object_detection/dataset/ds_gc/swimlane_train/"
SWIM_TEST = "/content/gdrive/My Drive/TF/models/research/object_detection/dataset/ds_gc/swimlane_test/"

bpnm_train_dir = os.listdir(BPNM_TRAIN)[:128]
swimlane_train_dir = os.listdir(SWIM_TRAIN)

bpnm_test_dir = os.listdir(BPNM_TEST)
swimlane_test_dir = os.listdir(SWIM_TEST)


def create_features(img):
    cf = img.flatten()
    grey_img = rgb2grey(img)
    hogf = hog(grey_img, block_norm='L2-Hys', pixels_per_cell=(16, 16))
    flattened = np.hstack([cf, hogf])
    return flattened


bpnm_train = []
bpnm_test = []
swim_train = []
swim_test = []

for i in bpnm_train_dir:
    image = Image.open(BPNM_TRAIN + i)
    data = np.asarray(image)
    features = create_features(data)
    bpnm_train.append(features)

for i in swimlane_train_dir:
    image = Image.open(SWIM_TRAIN + i)
    data = np.asarray(image)
    features = create_features(data)
    swim_train.append(features)


for i in bpnm_test_dir:
    image = Image.open(BPNM_TEST + i)
    data = np.asarray(image)
    features = create_features(data)
    bpnm_test.append(features)


for i in swimlane_test_dir:
    image = Image.open(SWIM_TEST + i)
    data = np.asarray(image)
    features = create_features(data)
    swim_test.append(features)

bpnm_train = np.array(bpnm_train)
bpnm_test = np.array(bpnm_test)
swim_train = np.array(swim_train)
swim_test = np.array(swim_test)

ss = StandardScaler()

bpnm_std_train = ss.fit_transform(bpnm_train)
pca_bpnm_train = PCA(n_components=32)
bpnm_train = pca_bpnm_train.fit_transform(bpnm_std_train)

bpnm_std_test = ss.fit_transform(bpnm_test)
pca_bpnm_test = PCA(n_components=32)
bpnm_test = pca_bpnm_test.fit_transform(bpnm_std_test)

swim_std_train = ss.fit_transform(swim_train)
pca_swim_train = PCA(n_components=32)
swim_train = pca_swim_train.fit_transform(swim_std_train)

swim_std_test = ss.fit_transform(swim_test)
pca_swim_test = PCA(n_components=32)
swim_test = pca_swim_test.fit_transform(swim_std_test)

bpnm_train_y = [1 for i in range(len(bpnm_train))]
bpnm_test_y = [1 for i in range(len(bpnm_test))]

swim_train_y = [0 for i in range(len(swim_train))]
swim_test_y = [0 for i in range(len(swim_test))]

train_x = np.concatenate((bpnm_train, swim_train))
train_y = np.array(bpnm_train_y + swim_train_y)

test_x = np.concatenate((bpnm_test, swim_test))
test_y = np.array(bpnm_test_y + swim_test_y)

new_train_x, new_train_y = [], []
new_test_x, new_test_y = [], []

train = list(zip(train_x, train_y))
test = list(zip(test_x, test_y))
random.shuffle(train)
random.shuffle(test)

train_x = [i[0] for i in train]
train_y = [i[-1] for i in train]

test_x = [i[0] for i in test]
test_y = [i[-1] for i in test]

train_x = np.array(train_x)
train_y = np.array(train_y)
test_x = np.array(test_x)
test_y = np.array(test_y)

SAVE_LOC = "/content/gdrive/My Drive/TF/models/research/object_detection/dataset/ds_gc/"
np.save(SAVE_LOC + "train_x.npy", train_x)
np.save(SAVE_LOC + "train_y.npy", train_y)
np.save(SAVE_LOC + "test_x.npy", test_x)
np.save(SAVE_LOC + "test_y.npy", test_y)

"""## Linear Classifier 

"""


def normalize_feature(X):
    mean = np.mean(X)
    X_norm = X - mean
    return X_norm


def get_gaussian_kernel(x1, x2, sigma=1):
    d = np.subtract(x1, x2)
    d_sqrd = np.dot(d, d)

    denom = 2*(sigma**2)
    res = -(d_sqrd/denom)

    return np.exp(res)


def minimize_obj(weights):
    return np.linalg.norm(weights)


def train_ksvm(kernel, X, y, x_test):
    X = normalize_feature(X)
    x_test = normalize_feature(x_test)
    m, n = X.shape

    test_m, test_n = xtest.shape
    features = np.zeros((m, m))
    features_test = np.zeros((test_m, test_m))

    for i in range(m):
        for j in range(m):
            features[i, j] = kernel(X[i], X[j])

    features = np.hstack((np.ones((features.shape[0], 1)), features))

    for i in range(mTest):
        for j in range(m):
            features_test[i, j] = kernel(xtest[i], X[j])

    features_test = np.hstack(
        (np.ones((features_test.shape[0], 1)), features_test))

    constraint = ({'type': 'ineq', 'fun': lambda w: np.multiply(
        y, np.matmul(features, w)) - 1})
    theta = np.zeros((features.shape[1]))
    minimized = minimize(minimize_obj, theta,
                         method='SLSQP', constraints=constraint)
    res_theta = minimized.x

    preds = np.sign(np.matmul(features_test, res_theta))
    return res_theta, preds


svm = SVC(kernel='linear', probability=True, random_state=42)
svm.fit(train_x, train_y)

filename = "/content/gdrive/My Drive/TF/models/research/object_detection/trained_models/ksvm_model.sav"
pickle.dump(svm, open(filename, 'wb'))

y_pred = svm.predict(test_x)
accuracy = accuracy_score(test_y, y_pred)
print('Model accuracy is: ', accuracy)

test1, preds1 = train_ksvm(get_gaussianKern, train_x, train_y, test_x)
plot_confusion_matrix(preds1, test_y)
