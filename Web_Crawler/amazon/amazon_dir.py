import requests
from bs4 import BeautifulSoup
import time
import re
from multiprocessing import Pool
from pymongo import MongoClient

dir_url = 'https://www.amazon.cn/gp/site-directory?ie=UTF8&ref_=nav_deepshopall_variant_fullstore_l1'
headers = {'User-Agent':'Mozilla/5.0\
 (Windows NT 10.0; Win64; x64)Apple\
 WebKit/537.36 (KHTML, like Gecko)\
  Chrome/77.0.3865.90 Safari/537.36'}     #浏览器头信息
# proxies = {'https':'171.35.167.25'}

client = MongoClient('mongodb://localhost:27017/')
db = client['amazon']
myset = db.amazon_dir_info

def download(url):
    r = requests.get(dir_url,headers=headers)
    if(r.status_code == 200):
        print("商品目录页下载成功！")
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup
    else:
        print("下载失败")
        exit(0)

def parse(soup):
    datas = soup.find_all(class_='nav_a a-link-normal a-color-base')
    for data in datas:
        good_type = data.text
        good_url = "https://www.amazon.cn"+data['href']
        info = {
            'good_type':good_type,
            'good_url':good_url
        }
        print(str(info))
        myset.insert_one(info)
        print("插入成功！")

if __name__ =="__main__":
    soup = download(dir_url)
    parse(soup)
