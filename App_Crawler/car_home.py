'''
汽车之家极速版app中的数据爬取
拦截脚本
推荐、新闻、评测、猎奇、车圈女神、购车、用车养车、改装、自驾游、摩托车
'''
import pymongo
import json
from mitmproxy import ctx
import hashlib
import redis
from xml.dom.minidom import parseString
from urllib3.response import GzipDecoder
# from loguru import logger
import datetime
from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017/')
db = client['car_home']
myset = db.car_home_speed

# #连接数据库db0
# r = redis.Redis(host='127.0.0.1', port=6379,db=0)
#
# # 使用连接池连接数据库。这样就可以实现多个Redis实例共享一个连接池
# pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
# #创建一个redis实例
# r = redis.Redis(connection_pool=pool)


#从响应流中获取数据
def response(flow):
    """汽车之家"""
    #20.9.28补充广告链接
    #广告
    #
    if ('AdvertiseService/AppHandler.ashx?' in flow.request.url):
        ctx.log.alert(str(flow.request.url))
        try:
            text = flow.response.text
            data = json.loads(text)
            adlist = data.get('result').get('list')
            title = ''
            url = ''
        except:
            ctx.log.alert('出错了')
        for rs in adlist:
            if('addata' in rs):
                data = rs.get('addata')
                if('title' in data):
                    title = data.get('title').get('src')
                info = {
                    'tag': '汽车之家',
                    'title': title,
                    'url': '',
                    '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
                }
                ctx.log.alert(str(info))
                # r.set('car_home',title,url)

    # 推荐
    if 'speed/index?' in flow.request.url:
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('list')
        for rs in newslist:
            data = rs
            title = data.get('title')
            url = data.get('shareurl')
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            # r.hset('car_home', str(title), str(url))
            # insert_mongo(info)
            if(title is not None):
                myset.insert_one(info)

    # 新闻 and 测评 and 猎奇 and 车圈女神 and 购车 and 用车养车 and 改装 and 自驾游 and 摩托车
    if 'speed/tagfeed?' in flow.request.url:
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('list')
        for data in newslist:
            title = data.get('title')
            url = data.get('shareurl')
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            # r.hset('car_home', str(title), str(url))
            # insert_mongo(info)
            if(title is not None):
                myset.insert_one(info)