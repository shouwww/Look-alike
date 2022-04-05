#!/usr/bin/env python
# -*- coding: utf-8 -*-

from icrawler.builtin import BingImageCrawler


def get_images_icrew(keyword: str, save_dir: str, max_num: int):
    crawler = BingImageCrawler(storage={'root_dir': save_dir})
    crawler.crawl(keyword=keyword, max_num=max_num)
# End def


def main():
    get_images_icrew('ラファエル', 'img/ラファエル', 100)


if __name__ == "__main__":
    main()
