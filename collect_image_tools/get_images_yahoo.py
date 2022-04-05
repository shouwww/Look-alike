# coding: utf-8
#
# https://karaage.hatenadiary.jp/entry/2017/08/23/073000
# 
# yahooの画像検索の結果上位60枚を取得する

import os
import sys
import traceback
from mimetypes import guess_extension
from time import time, sleep
from urllib.request import urlopen, Request
from urllib.parse import quote
from bs4 import BeautifulSoup

MY_EMAIL_ADDR = 'uw0516sho@gmail.com'


class Fetcher:
    def __init__(self, ua=''):
        self.ua = ua

    def fetch(self, url):
        req = Request(url, headers={'User-Agent': self.ua})
        try:
            with urlopen(req, timeout=3) as p:
                b_content = p.read()
                mime = p.getheader('Content-Type')
        except:
            sys.stderr.write('Error in fetching {}\n'.format(url))
            sys.stderr.write(traceback.format_exc())
            return None, None
        return b_content, mime

fetcher = Fetcher(MY_EMAIL_ADDR)

def fetch_and_save_img(word):
    data_dir = 'data/'+ word + '/imgs_yahoo/'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    for i, img_url in enumerate(img_url_list(word)):
        sleep(0.5)
        img, mime = fetcher.fetch(img_url)
        if not mime or not img:
            continue
        ext = guess_extension(mime.split(';')[0])
        if ext in ('.jpe', '.jpeg', '.png', '.gif'):
            ext = '.jpg'
        if not ext:
            continue
        result_file = os.path.join(data_dir, str(i) + ext)
        with open(result_file, mode='wb') as f:
            f.write(img)
        print('fetched No.',i ,"URL=", img_url)


def img_url_list(word):
    """
    using yahoo (this script can't use at google)
    """
    url = 'http://image.search.yahoo.co.jp/search?n=100&p={}&search.x=1'.format(quote(word))
    byte_content, _ = fetcher.fetch(url)
    structured_page = BeautifulSoup(byte_content.decode('UTF-8'), 'html.parser')
    img_link_elems = structured_page.find_all('a', attrs={'target': 'imagewin'})
    img_urls = [e.get('href') for e in img_link_elems if e.get('href').startswith('http')]
    img_urls = list(set(img_urls))
    print("image URL list Len = ",len(img_urls))

    return img_urls

if __name__ == '__main__':
    '''
    word = sys.argv[1]
    fetch_and_save_img(word)
    '''
    word = "竹達彩奈"
    fetch_and_save_img(word)
    word = "悠木碧"
    fetch_and_save_img(word)
    word = "プチミレディ"
    fetch_and_save_img(word)