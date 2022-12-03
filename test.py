from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from starlette import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from urllib import request
from skimage.metrics import structural_similarity as ssim
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from scipy.spatial import distance

import time
import pickle
import os
import cv2
import numpy as np
import matplotlib.pylab as plt
import itertools
import mahotas as mh
import numpy as np
import matplotlib.pyplot as plt

def mahotas_test():
    features = []

    images = os.listdir("./img")
    images = tuple(filter(lambda x: ".png" in x, images))
    images = tuple(map(lambda x: "./img/" + x, images))

    for image in images:
        img = mh.imread(image)
        if len(img.shape) <= 2:
            continue
        if img.shape[2] != 3:
            img = mh.imresize(img, (img.shape[0], img.shape[1], 3))

        img = mh.colors.rgb2gray(img, dtype=np.uint8)
        features.append(mh.features.haralick(img).ravel())

    features = np.array(features)

    clf = Pipeline([('preproc', StandardScaler()), ('classifier', LogisticRegression())])

    sc = StandardScaler()
    features = sc.fit_transform(features)

    dists = distance.squareform(distance.pdist(features))

    return dists, images


def selectimage(n, m, dists, images):
    # image_position = dists[n][dists[n] < 0.01].argsort()[m]
    image_position = dists[n].argsort()[m]

    print(image_position, dists[n][image_position])

    # print(dists[n])
    # print()
    # print(dists[n][dists[n] < 10])
    # print(dists[n][dists[n] < 10].argsort())

    image = mh.imread(images[image_position])
    return image


def plotImages(n):
    SHOW_NUM = 10
    dists, images = mahotas_test()

    # print(dists[n])
    dists = dists / np.sqrt(np.sum(dists**2))
    # print(dists[n])

    fig, ax = plt.subplots(1, SHOW_NUM, figsize = (15, 5))
    
    ax[0].imshow(mh.imread(images[n]))
    ax[0].set_xticks([])
    ax[0].set_yticks([])

    for i in range(1, SHOW_NUM+1):
        try:
            ax[i].imshow(selectimage(n, i, dists, images))
            ax[i].set_xticks([])
            ax[i].set_yticks([])
        except:
            continue
        
    plt.show()


for i in range(0, 1):
    plotImages(i)
