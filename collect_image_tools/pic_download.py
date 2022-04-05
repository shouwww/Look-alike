#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests
import re
import uuid
from bs4 import BeautifulSoup
from time import sleep
from tqdm import tqdm


url = "https://search.nifty.com/imagesearch/search?select=1&chartype=&q=%s&xargs=2&img.fmt=all&img.imtype=color&img.filteradult=no&img.type=all&img.dimensions=large&start=%s&num=20"
keyword = "竹達彩奈"
pages = [1]

for i in range(1, 100, 1):
    pages.append(i * 20)
# End if

count = 0
file_path = (str('./picture/') + keyword + str('/'))
if not os.path.exists(file_path):
    os.makedirs(file_path)
# End if

for q in tqdm(pages):
    r = requests.get(url % (keyword, q))
    soup = BeautifulSoup(r.text, 'lxml')
    imgs = soup.find_all('img', src=re.compile('^https://msp.c.yimg.jp/yjimage'))
    for img in imgs:
        r = requests.get(img['src'])
        with open(str('./picture/') + keyword + str('/') + str(uuid.uuid4()) + str('.jpeg'), 'wb') as file:
            file.write(r.content)
        # End with
    # End for
    sleep(1)
# End for
