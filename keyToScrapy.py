#！/user/bin/env python
# _*_ coding:utf-8 _*_


"""
在mongodb的keyword和brand中找到对应的关键词和品牌名 进行爬取
暂时用循环进行爬取
"""

from pymongo import MongoClient
import xianc_test
import time

conn = MongoClient('localhost', 27017)
db = conn.amazon

while True:
    start = time.time()
    keyword = db.keyword
    brand = db.brand

    keyword_list = [i['keyword'] for i in keyword.find()]
    brand_list = [i['brandName'] for i in brand.find()]

    '''
    for i in keyword_list+brand_list:
        print('正在爬取%s'%(i))
        xianc_test.scrapy(i)
    '''

    for brand in brand_list:
        print('正在爬取品牌名%s'%(brand))
        xianc_test.scrapy(brand, 'brand')

    for key in keyword_list:
        print('正在爬取关键词%s'%(key))
        xianc_test.scrapy(key, 'keyWord')
	
    end = time.time()
    throught = int(end-start)
    if throught < 86400*2:
        time.sleep(86400*2-throught)
