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


# ファイルの場所やラベル名の取得
data_dir = "img"
files = os.listdir(data_dir)
face_names = [f for f in files if os.path.isdir(os.path.join(data_dir, f))]
print(face_names)
print(len(face_names))

# 画像の補正パラメータ
# リサイズ
IMG_SIZE = 64

# トレーニングデータの生成
training_data = []
x_train = []
x_test = []
y_train = []
y_test = []
num_testdata = 30


def create_training_data():
    class_dict = {}
    for class_num, face_name in enumerate(face_names):
        class_dict[face_name] = class_num
        path = os.path.join(data_dir, face_name)
        files = glob.glob(path + '/e_*.jpg')
        for i, img_file_path in enumerate(files):
            try:
                # 画像読み込み
                img_array = imread(img_file_path, cv2.COLOR_BGR2RGB)
                # 画像のリサイズ
                img_resize_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
                # 画像データ、ラベル情報を追加
                if i < num_testdata:
                    x_test.append(img_resize_array)
                    y_test.append(class_num)
                else:
                    x_train.append(img_resize_array)
                    y_train.append(class_num)
                # training_data.append([img_resize_array, class_num])
            except Exception as e:
                print('error')
                print(e)
                pass
    # np arrayにへんかん
    # 作成されたデータの確認

    print('========トレーニングデータ==========')
    print(f'トレーニングデータ 画像: {len(x_train)}')
    print(f'トレーニングデータ ラベル: {len(y_train)}')
    print(f'テストデータ 画像: {len(x_test)}')
    print(f'テストデータ ラベル: {len(y_test)}')
    with open('model/class_name.json','wb') as fp:
        pickle.dump(class_dict, fp)
# End def


# トレーニングデータ生成の実行
x_train = []
x_test = []
y_train = []
y_test = []
create_training_data()
x_train = np.array(x_train)
x_test = np.array(x_test)
y_train = np.array(y_train)
y_test = np.array(y_test)
print(f'トレーニングデータ 画像 数,縦,横,チャネル : {x_train.shape}')
print(f'テストデータ       画像 数,縦,横,チャネル : {x_test.shape}')
print(f'トレーニングデータ ラベル 数 : {y_train.shape}')
print(f'テストデータ       ラベル 数 : {y_test.shape}')

# 学習データを読み込む

# 入力データの各画素値を0-1の範囲で正規化する
x_train = x_train.astype('float') / 255
x_test = x_test.astype('float') / 255
# to_categorical()にてラベルをone hot vector化
class_num = len(face_names)
y_train = np_utils.to_categorical(y_train, class_num)
y_test = np_utils.to_categorical(y_test, class_num)


def train(x, y, x_test, y_test):
    model = Sequential()
    # xは(170, 128, 128, 3)
    # x.shape[1:]で(128,128,3)で入力にできる
    model.add(Conv2D(32, (3, 3), padding='same', input_shape=x.shape[1:]))
    model.add(Activation('relu'))
    model.add(Conv2D(32, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.1))

    model.add(Conv2D(64, (3, 3), padding='same'))
    model.add(Activation('relu'))
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dropout(0.45))
    #model.add(Dense(34))
    model.add(Dense(len(face_names)))
    model.add(Activation('softmax'))

    # https://keras.io/ja/optimizers/
    # 今回は、最適化アルゴリズムにRMSpropを利用
    opt = RMSprop(lr=0.00005, decay=1e-6)
    # https://keras.io/ja/models/sequential/
    model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
    model.fit(x, y, validation_data=(x_test, y_test), batch_size=50, epochs=300, verbose=2)
    # HDF5ファイルにKerasのモデルを保存
    model.save('model/cnn.h5')
    return model
# End def

from keras.utils import plot_model
model = train(x_train, y_train, x_test, y_test)
# モデルの概要を表示
model.summary()
# モデルを図として出力
plot_model(model, to_file='model/cnn_model.png', show_shapes=True, show_layer_names=True)
