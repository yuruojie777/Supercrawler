import requests
from bs4 import BeautifulSoup
import re
from pymongo import MongoClient
import time
import hashlib
from loguru import logger
from requests.cookies import RequestsCookieJar

headers = {'User-Agent':'Mozilla/5.0\
 (Windows NT 10.0; Win64; x64)Apple\
 WebKit/537.36 (KHTML, like Gecko)\
  Chrome/77.0.3865.90 Safari/537.36'}     #浏览器头信息

client = MongoClient('mongodb://localhost:27017/')
db = client['amazon']
ebook_set = db.amazon_ebook_info


url = 'https://www.amazon.cn/Kindle%E7%94%B5%E5%AD%90%E4%B9%A6-%E5%B0%8F%E8%AF%B4/b/457-3985918-5598006?ie=UTF8&node=144154071&ref_=sd_allcat_kindle_l3_b144154071'
urls = set()
urls.add(url)
s = requests.session()
# cookie = requests.get(url,headers=headers).cookies
# cookie_jar = RequestsCookieJar()
# cookie_jar.set("BAIDUID", "4EDT7A5263775F7E0A4B&F330724:FG=1", domain="baidu.com")
#
# cookie = requests.get(url,headers=headers).cookies
# for key,value in cookie.items():
#     print(key+":"+value)
def insert_mongo(info):
    try:
        collection = db['amazon_ebook_info']
        collection.insert_one(info)
        logger.warning('insert 成功！%s' % info)
    except Exception as err:
        logger.error('%s - %s' % (err, info))


def crawl(urls):
    if(len(urls)!=0):
        url = urls.pop()
        r = s.get(url, headers=headers)
        if(r.status_code == 200):
            r = r.text
            print("下载页面内容成功")
        datas = BeautifulSoup(r, 'html.parser')
        if ('ref_=sd_allcat_kindle_l3_b144154071' in url):
            soup = datas.find_all(id=re.compile('result_.+?'))
            for i in soup:
                for data in i:
                    title = data.find(class_='a-link-normal s-access-detail-page s-color-twister-title-link a-text-normal').text
                    price = data.find(class_='a-size-base a-color-price s-price a-text-bold').text
                    info = {
                        "_id": hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest(),
                        'title': title,
                        'url': url,
                        'price': float(price.replace('￥', ''))
                    }
                    # print(str(info))
                    insert_mongo(info)
                    # print("插入成功！")
            next_url = datas.find_all(class_='pagnNext')[0]['href']
            next_url = 'https://www.amazon.cn' + next_url
            print(next_url)
            urls.add(next_url)
            time.sleep(30)
        else:
            soup = BeautifulSoup(r, 'html.parser').find_all("div", attrs={"data-component-type": "s-search-result"})
            for data in soup:
                title = data.find(class_="a-link-normal a-text-normal").text
                url = 'https://www.amazon.cn'+data.find(class_="a-link-normal a-text-normal")['href']
                price = data.find(class_='a-offscreen').text.replace('￥','')
                info = {
                    "_id": hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest(),
                    'title': title.replace(r'\n',''),
                    'url': url,
                    'price': (price.replace('￥', ''))
                }
                # print(str(info))
                insert_mongo(info)
                # print("插入成功！")
            try:
                next_url_content = BeautifulSoup(r, 'html.parser').find_all("li", class_='a-last')[0]
                # print(next_url_content)
                next_url = "https://www.amazon.cn" + next_url_content.find('a').get('href')
                # print(next_url)
                urls.add(next_url)
            except:
                print("页面加载不完全")
                print(r)
                exit(0)
            time.sleep(30)
    else:
        exit(0)

def scedu():
    page = 1
    while True:
        print("正在处理第"+str(page)+"页")
        crawl(urls)
        page = page+1

if __name__ =="__main__":
    scedu()




# // *[ @ id = "result_0"] / div / div / div / div[2] / div[2] / div[1] / div[2] / a / span[2]