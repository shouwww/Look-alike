#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import os
import glob
import cv2
import random
import numpy as np
import pickle
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras.optimizers import RMSprop # TensorFlow1系
# from keras.optimizers import RMSprop # エラー（ImportError: cannot import name 'RMSprop' from 'keras.optimizers' (/usr/local/lib/python3.7/dist-packages/keras/optimizers.py)）が発生
# from tensorflow.keras.optimizers import RMSprop # TensorFlow2系
from keras.utils import np_utils
import keras

# 推論
from keras.models import load_model


# cv2日本語パス対策
def imread(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None


# cv2日本語パス対策
def imwrite(filename, img, params=None):
    try:
        ext = os.path.splitext(filename)[1]
        result, n = cv2.imencode(ext, img, params)

        if result:
            with open(filename, mode='w+b') as f:
                n.tofile(f)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def get_key_from_value(d, val):
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None

# 画像の補正パラメータ
# リサイズ
IMG_SIZE = 64
imsize = (IMG_SIZE, IMG_SIZE)
test_image_paths = ['test1.jpg','test2.jpg','test3.jpg']
keras_param = 'model/cnn.h5'
with open('model/class_name.json','rb') as fp:
    class_dict = pickle.load(fp)
print(class_dict)

def load_img(path):
    # 画像読み込み
    img_array = imread(path, cv2.COLOR_BGR2RGB)
    # 画像のリサイズ
    img_resize_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
    # 画像をnumpy配列に変換
    img_np = np.asarray(img_resize_array)
    # 正規化
    img_np = img_np / 255.0
    return img_np
# End def

model = load_model(keras_param)

for test_img_path in test_image_paths:
    img = load_img(test_img_path)
    predictions = model.predict(np.array([img]))
    print('推論精度の表示')
    print(test_img_path)
    print(predictions[0])
    results = predictions.argmax(axis=1)
    print(results)
    print(get_key_from_value(class_dict, results[0]))
