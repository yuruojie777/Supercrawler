import requests
from bs4 import BeautifulSoup
import time
import re
from multiprocessing import Pool
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['amazon']
myset = db.amazon_computer_info

url = 'https://www.amazon.cn/s?rh=n%3A106200071&page='

headers = {'User-Agent':'Mozilla/5.0\
 (Windows NT 10.0; Win64; x64)Apple\
 WebKit/537.36 (KHTML, like Gecko)\
  Chrome/77.0.3865.90 Safari/537.36'}     #浏览器头信息
# proxies = {'https':'171.35.167.25'}

def parse_data(soup):
    # if (url == 'https://www.amazon.cn/s?rh=n%3A106200071&page='):
    datas = soup.find_all(class_='a-section a-spacing-medium')
    flag = 0
    for data in datas:
        title = data.find_all(class_="a-link-normal a-text-normal")[0].text.replace('\n', '')
        price = data.find_all(class_="a-price-whole")[0].text + data.find_all(class_="a-price-fraction")[0].text
        url = data.find_all(class_="a-link-normal a-text-normal")[0]['href']
        info = {
            'title': title,
            'price': float(price.replace(',','')),
            'url': "https://www.amazon.cn/"+url
        }
        if(info!=None):
            print("解析成功")
            print(str(info))
            myset.insert_one(info)
            print("插入成功！")
            flag = 1
        else:
            print("解析出错")
            flag = 0
    return flag

def download(page):
    print("正在下载第"+str(page)+"页")
    print(url+str(page))
    r = requests.get(url+str(page),headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    if(r.text!=None):
        return soup
    else:
        print("页面未成功下载")

def turn_page(total_page):
    for page in range(1,total_page+1):
        soup = download(str(page))
        time.sleep(5)
        if(parse_data(soup)):
            print("成功！")
        else:
            parse_data(soup)
        time.sleep(5)

if __name__ == "__main__":
    turn_page(40)