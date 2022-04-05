#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import os
import glob
import cv2
import random
import numpy as np
import math


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


# 画像の余白を白く塗りつぶして正方形に加工する関数
def whiten_margins(img):
    # 画像の縦横サイズを取得
    height, width, color = img.shape

    if height > width:
        # 縦長画像→幅を拡張する
        diffsize = height - width
        # 元画像を中央ぞろえにしたいので、左右に均等に余白を入れる
        padding_half = int(diffsize / 2)
        padding_img = cv2.copyMakeBorder(img, 0, 0, padding_half, padding_half, cv2.BORDER_CONSTANT, (0, 0, 0))
    elif width > height:
        # 横長画像→高さを拡張する
        diffsize = width - height
        padding_half = int(diffsize / 2)
        padding_img = cv2.copyMakeBorder(img, padding_half, padding_half, 0, 0, cv2.BORDER_CONSTANT, (0, 0, 0))
    else:
        padding_img = img
    return padding_img
# End def


def face_detector(img_path: str, IMG_SIZE: int):
    print_str = ''
    haar_path = 'tools/haarcascades/haarcascade_frontalface_alt.xml'
    eye_cascade_path = 'tools/haarcascades/haarcascade_eye.xml'
    # ファイル名(拡張子なしを取得)
    basename_without_ext = os.path.splitext(os.path.basename(img_path))[0]
    basename_ext = os.path.splitext(os.path.basename(img_path))[1]
    dirname = os.path.dirname(img_path)
    # カスケード型分類に使用するデータ(xmlファイル)の読み込み
    cascade = cv2.CascadeClassifier(haar_path)
    eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
    # 画像ファイルの読み込み
    # img = cv2.imread(img_path)
    img = imread(img_path)
    # グレースケール変換
    # img_g = cv2.imread(img_path, 0)
    img_g = imread(img_path, 0)
    # カスケード型分類気を使用して顔部分を検出
    # face = cascade.detectMultiScale(img_g, scaleFactor=1.1, minNeighbors=6, minSize=(100, 100))
    face = cascade.detectMultiScale(img_g, minSize=(100, 100))
    print('顔検出座標確認')
    print(f'顔検出数 : {len(face)}')
    eyes = [[1,1,1,1]]
    save_path=''
    # 顔画像切り抜き
    if len(face) > 0:
        if len(face) > 1:
            # 顔が複数ある場合は別のフォルダに入れる
            dirname = os.path.join(dirname, 'incomplete')
            if not os.path.exists(dirname):
                os.makedirs(dirname)
        for i, [x, y, w, h] in enumerate(face):
            save_file_name = 'e_' + basename_without_ext + '_' + str(i) + '.jpg'    # basename_ext
            save_path = os.path.join(dirname, save_file_name)
            face_cut_g = img_g[y: y + h, x: x + w]
            eyes = eye_cascade.detectMultiScale(face_cut_g)
            if len(eyes) > 1:
                face_cut = img[y: y + h, x: x + w]
                # if(os.path.isfile(save_path)):
                #    os.remove(save_path)
                face_cut_whiten = whiten_margins(face_cut)
                face_cut_resize_whiten = cv2.resize(face_cut_whiten, dsize=(IMG_SIZE, IMG_SIZE))

                # cv2.imwrite(save_path, face_cut_resize_whiten)
                imwrite(save_path, face_cut_resize_whiten)
        # End for
    # End if
    print(f'顔検出数:{len(face)}__目:{len(eyes)}__save img : {save_path}')
# End def


def main():
    files = os.listdir('img')
    img_dir_list = [f for f in files if os.path.isdir(os.path.join('img', f))]
    print(img_dir_list)
    for img_dir in img_dir_list:
        f_img_dir = os.path.join('img', img_dir)
        for img_path in glob.iglob(f_img_dir + '/*'):
            print(f'load image path : {img_path}')
            if 'e_' in img_path:
                print(f'pass : {img_path}')
                continue
            else:
                face_detector(img_path, 128)
            # End if
        # End for
    # End for


if __name__ == "__main__":
    main()