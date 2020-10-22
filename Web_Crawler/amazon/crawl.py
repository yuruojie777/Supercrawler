import requests
from bs4 import BeautifulSoup
import time
import re
from multiprocessing import Pool
from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017/')
db = client['amazon']
good_dir = db.amazon_dir_info
url_set = dict()

headers = {'User-Agent':'Mozilla/5.0\
 (Windows NT 10.0; Win64; x64)Apple\
 WebKit/537.36 (KHTML, like Gecko)\
  Chrome/77.0.3865.90 Safari/537.36'}     #浏览器头信息

def get_url():
    for data in good_dir.find():
        url_set[data['good_type']]=data['good_url']

# get_url()
# for good_type,good_url in url_set.items():
#     print(good_type,good_url)


def download(url):
    r = requests.get(url,headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    if(soup!=None):
        print("页面下载成功！")
        return url,soup
    else:
        print("下载页面失败！")
