#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from typing import List
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import os
import time
import datetime
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException


tm_start = time.time()            # 処理時間計測用
dt_now = datetime.datetime.now()  # 現在日時
dt_date_str = dt_now.strftime('%Y/%m/%d %H:%M')


def image_collect(quert_words: List[str], limit_num: int):
    """
        与えられた文字列をgoogle画像検索をし、画像を取得する。検索文字列はリスト形式で0要素目に人の名前、1要素目以降にサブワードを入れる

        Parameters
        ----------
        quest_word: List[str]
            画像を検索したい人の名前など
            e.x. ['織田信長']
            e.x. ['豊臣秀吉','かっこいい']
        limit_num: int
            取得する画像の上限(※枚数が指定できるわけではない)

        Returns
        -------
        None
    """

    QUERY = ' '.join(quert_words)   # 検索ワード
    LIMIT_DL_NUM = limit_num  # ダウンロード数の上限
    SAVE_DIR = '../img/' + quert_words[0]   # 出力フォルダへのパス（フォルダがない場合は自動生成する）
    FILE_NAME = quert_words[0] + '_'    # ファイル名（ファイル名の後ろに０からの連番と拡張子が付く）
    TIMEOUT = 60        # 要素検索のタイムアウト（秒）
    ACCESS_WAIT = 1     # アクセスする間隔（秒）
    RETRY_NUM = 3       # リトライ回数（クリック、requests）
    # DRIVER_PATH = '/usr/bin/chromedriver'       # chromedriver.exeへのパス

    # Chromeをヘッドレスモードで起動
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--start-fullscreen')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-extensions')
    # driver = webdriver.Chrome(DRIVER_PATH, options=options)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    # ダウンロードしたURLリストを読み込む。
    path = '_url.txt'
    downloaded_list = []
    if os.path.exists(path):
        f = open(path, 'r', encoding='utf-8', newline='\n')
        datalists = f.read().splitlines()
        for line in datalists:
            split_line = line.split(':', 1)
            downloaded_list.append(split_line[1])
        f.close()
        print(f'ダウンロードリスト: length:{len(downloaded_list)}')
        print(downloaded_list)
    else:
        print('ダウンロードリストがありません')
    # タイムアウト設定
    driver.implicitly_wait(TIMEOUT)

    tm_driver = time.time()
    print('WebDriver起動完了', f'{tm_driver - tm_start:.1f}s')

    # Google画像検索ページを取得
    url = f'https://www.google.com/search?q={QUERY}&tbm=isch'
    driver.get(url)

    tm_geturl = time.time()
    print('Google画像検索ページ取得', f'{tm_geturl - tm_driver:.1f}s')

    tmb_elems = driver.find_elements_by_css_selector('#islmp img')
    tmb_alts = [tmb.get_attribute('alt') for tmb in tmb_elems]

    count = len(tmb_alts) - tmb_alts.count('')
    print(count)

    while count < LIMIT_DL_NUM:
        # ページの一番下へスクロールして新しいサムネイル画像を表示させる
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(0.5)

        # サムネイル画像取得
        tmb_elems = driver.find_elements_by_css_selector('#islmp img')
        tmb_alts = [tmb.get_attribute('alt') for tmb in tmb_elems]

        count = len(tmb_alts) - tmb_alts.count('')
        print(count)

    # サムネイル画像をクリックすると表示される領域を取得
    imgframe_elem = driver.find_element_by_id('islsp')

    # 出力フォルダ作成
    os.makedirs(SAVE_DIR, exist_ok=True)
    # HTTPヘッダ作成
    HTTP_HEADERS = {'User-Agent': driver.execute_script('return navigator.userAgent;')}
    print(HTTP_HEADERS)
    # ダウンロード対象のファイル拡張子
    IMG_EXTS = ('.jpg', '.jpeg', '.png', '.gif')

    # 拡張子を取得
    def get_extension(url):
        url_lower = url.lower()
        for img_ext in IMG_EXTS:
            if img_ext in url_lower:
                extension = '.jpg' if img_ext == '.jpeg' else img_ext
                break
        else:
            extension = ''
        return extension

    # urlの画像を取得しファイルへ書き込む
    def download_image(url, path, loop):
        result = False
        for i in range(loop):
            try:
                r = requests.get(url, headers=HTTP_HEADERS, stream=True, timeout=10)
                r.raise_for_status()
                with open(path, 'wb') as f:
                    f.write(r.content)

            except requests.exceptions.SSLError:
                print('***** SSL エラー')
                break  # リトライしない
            except requests.exceptions.RequestException as e:
                print(f'***** requests エラー({e}): {i + 1}/{RETRY_NUM}')
                time.sleep(0.5)
            else:
                result = True
                break  # try成功
        return result

    tm_thumbnails = time.time()
    print('サムネイル画像取得', f'{tm_thumbnails - tm_geturl:.1f}s')

    # ダウンロード
    EXCLUSION_URL = 'https://lh3.googleusercontent.com/'  # 除外対象url
    count = 0
    url_list = []
    for tmb_elem, tmb_alt in zip(tmb_elems, tmb_alts):
        if tmb_alt == '':
            continue
        print(f'{count}: {tmb_alt}')
        for i in range(RETRY_NUM):
            try:
                # サムネイル画像をクリック
                tmb_elem.click()
            except ElementClickInterceptedException:
                print(f'***** click エラー: {i + 1}/{RETRY_NUM}')
                driver.execute_script('arguments[0].scrollIntoView(true);', tmb_elem)
                time.sleep(0.5)
            else:
                break  # try成功
        else:
            print('***** キャンセル')
            continue  # リトライ失敗
        # End for
        # アクセス負荷軽減用のウェイト
        time.sleep(ACCESS_WAIT)
        alt = tmb_alt.replace("'", "\\'")
        try:
            img_elem = imgframe_elem.find_element_by_css_selector(f'img[alt=\'{alt}\']')
        except NoSuchElementException:
            print('***** img要素検索エラー')
            print('***** キャンセル')
            continue
        # url取得
        tmb_url = tmb_elem.get_attribute('src')  # サムネイル画像のsrc属性値
        for i in range(RETRY_NUM):
            url = img_elem.get_attribute('src')
            if EXCLUSION_URL in url:
                print('***** 除外対象url')
                url = ''
                break
            elif url in downloaded_list:
                print('***** ダウンロード済みURLです')
                url = ''
                break
            elif url == tmb_url:  # src属性値が遷移するまでリトライ
                print(f'***** urlチェック: {i + 1}/{RETRY_NUM}')
                time.sleep(1)
                url = ''
            else:
                break
            # End if
        # End for
        if url == '':
            print('***** キャンセル')
            continue
        # End if
        # 画像を取得しファイルへ保存
        ext = get_extension(url)
        if ext == '':
            print(f'***** urlに拡張子が含まれていないのでキャンセル')
            print(f'{url}')
            continue
        # End if
        file_count = sum(os.path.isfile(os.path.join(SAVE_DIR, name)) for name in os.listdir(SAVE_DIR))
        filename = f'{FILE_NAME}{file_count}{ext}'
        path = SAVE_DIR + '/' + filename
        result = download_image(url, path, RETRY_NUM)
        if result is False:
            print('***** キャンセル')
            continue
        # End if
        url_list.append(f'{filename}:{url}')
        # ダウンロード数の更新と終了判定
        count += 1
        if count >= LIMIT_DL_NUM:
            break
        # End if
    tm_end = time.time()
    print('ダウンロード', f'{tm_end - tm_thumbnails:.1f}s')
    print('------------------------------------')
    total = tm_end - tm_start
    total_str = f'トータル時間: {total:.1f}s({total/60:.2f}min)'
    count_str = f'ダウンロード数: {count}'
    print(total_str)
    print(count_str)

    # urlをファイルへ保存
    path = '_url.txt'
    with open(path, 'a', encoding='utf-8') as f:
        f.write('\n'.join(url_list))
        f.write('\n')
    # End with
    driver.quit()


def main():
    quert_words = ['白石麻衣', '篠原涼子', '広瀬すず', '新垣結衣', '石原さとみ', '深田恭子', '桐谷美玲', '土屋太鳳', '佐々木希', '長澤まさみ', '指原莉乃', '井上真央', '川口春奈', '榮倉奈々', '本田翼', '堀北真希', '綾瀬はるか', '上戸彩', '広瀬アリス', '沢尻エリカ', '倉科カナ', '米倉涼子', '釈由美子', '戸田恵梨香', '相武紗季', '天海祐希', '菅野美穂', '川島海荷', '川栄李奈', '高岡早紀', '上野樹里', '松下奈緒', '及川奈央', '竹内結子', '中谷美紀', '黒木華', '白石美帆', '香里奈', '井川遥', '松嶋菜々子', '広末涼子', '仲里依紗']
    for quert_word in quert_words:
        image_collect([quert_word], 400)


if __name__ == "__main__":
    main()
