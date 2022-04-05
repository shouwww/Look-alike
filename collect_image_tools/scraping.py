# -*- coding='utf-8' -*-
#
# http://www.htmllifehack.xyz/entry/2017/09/04/224736
#
# URL に書いたURL中の画像を取得する。まとめページとかならいいかも

import requests # urlを読み込むためrequestsをインポート
from bs4 import BeautifulSoup # htmlを読み込むためBeautifulSoupをインポート

URL = ''　# ここにサイトのurlを貼る
images = []　# 画像を入れるためにリストを作る

soup = BeautifulSoup(requests.get(URL).content,'lxml')　# .contentでバイナリにする？

for link in soup.find_all("img"):　# imgタグを取得しlinkに入れる
    if link.get("src").endswith(".jpg"):　# imgタグの中の.jpgであるsrcタグを取得する
        images.append(link.get("src"))　# imagesリストに入れる

for target in images:　# リストはrequests.getで読めないようなので一旦targetに入れる
    resp = requests.get(target)
    with open('img/' + target.split('/')[-1], 'wb') as f:　# splitでファイル名を短縮する
        f.write(resp.content)　# 重要！.contentを入れないと画像データではなくtextデータになってしまう。
