import pymongo
import json
import re
from mitmproxy import ctx
import hashlib
import pymongo
from xml.dom.minidom import parseString
from urllib3.response import GzipDecoder
from loguru import logger

# 建立连接
client = pymongo.MongoClient("mongodb://localhost:27017/")
# 数据库名admin
db = client.car_home

def insert_mongo(info):
    try:
        collection = db['sov_car_home']
        collection.insert_one(info)
        logger.warning('insert 成功！%s' % info)
    except Exception as err:
        logger.error('%s - %s' % (err, info))


def parse_scheme(scheme):
    url = None
    data = scheme.split('&')
    for j in data[0].split('?'):
        ctx.log.alert(j)
    #根据scheme字段中的域名来判断访问链接的域名
    domain_name = data[0].split('?')[0]
    time = ''
    for i in data:
        # ctx.log.alert(i)
        if('lastupdatetime' in i):
            time = i.split('=')[1][0:5]+'/'


    if(len(data[0].split('?'))>1):
        id = data[0].split('?')[1].split('=')[1]
        if('id' in data[0].split('?')[1].split('=')[0]):
            if ('long' in domain_name or 'short' in domain_name):
                url = 'https://chejiahao.autohome.com.cn/info/' + str(id)
                ctx.log.alert(url)
            if ('articledetail' in domain_name):
                url = 'https://www.autohome.com.cn/advice/' + time + str(id) + '.html'
                ctx.log.alert(url)

            if ('video' in domain_name):
                url = 'http://chejiahao.m.autohome.com.cn/info/' + str(id)
                ctx.log.alert(url)

            if ('ricegroup' in domain_name):
                url = 'http://chejiahao.m.autohome.com.cn/fans/info/' + str(id)
                ctx.log.alert(url)
            # if('reputation' in domain_name):
            #     url = 'https://k.autohome.com.cn/spec/45081/'
            if('pictext'in domain_name):
                pass
            if('reputation' in domain_name):
                pass
            if('topic'in domain_name):
                pass

        if ('insidebrowser' in domain_name and 'url' in data[0].split('?')[1].split('=')[0]):
            from urllib import parse
            url = parse.unquote(data[0].split('?')[1].split('=')[1])
            ctx.log.alert(url)
    if url is not None:
        return url
    else:
        return None





def response(flow):
    # 20.9.28补充广告链接
    # 广告
    #
    if ('AdvertiseService/AppHandler.ashx?' in flow.request.url):
        ctx.log.alert(str(flow.request.url))
        text = flow.response.text
        data = json.loads(text)
        adlist = data.get('result').get('list')
        for rs in adlist:
            if ('addata' in rs):
                data = rs.get('addata')
                if ('title' in data):
                    title = data.get('title').get('src')
            if ('land' in rs):
                url = rs.get('land')
                info = {
                    'tag': '汽车之家',
                    'title': title,
                    'url': url,
                    '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
                }

                try:
                    collection = db['car_home_ad']
                    collection.insert_one(info)
                    logger.warning('insert 成功！%s' % info)
                except Exception as err:
                    logger.error('%s - %s' % (err, info))
    # 推荐
    # https://news.app.autohome.com.cn/shouye_v10.0.0/news/shouye.ashx?pm=2&cityid=440300&usercityid=110100&newstype=0&subjectids=&bi=1&showfocusimg=1&bsdata=eyJSZW1haW5EcUxlbiI6MCwicHZvcmRpbmEiOjEsInB2VGltZSI6MTU5MDQxNjU5NX0%3D&ratio=-1&devid=e1962bba_c20b_4d3f_a974_e8a5386c9860&op=1&net=5&gps=113.89365508051978%2C22.578934014852106&isonline=1&version=10.8.5&restart=0&channel=anzhi&pagesize=0&idfa=&os_version=8.1.0&gaid=&rnversion=3.0.0&abtest=android_homepagechangestyle%2Cnew%3Bandroid_homepagechangedata_new%2Cnew%3Bandroid_homepage_request_change%2Cnew%3Bandroid_homepage_change_style_threechannel%2Cnew%3B&uuid=u_188530069&devicetype=2&is818=0&useridvalue=7280ef4211be479e7012f943e42292c6&auth=83f4ff6d6f3446e59c8cabddbc1680080b3cbd95
    # url https://news.app.autohome.com.cn/cont_v10.0.0/cont/articlefinalpage?pm=2&newsid=996705&newstype=0&rct=0&version=19700101000000&abtest=use
    if 'shouye.ashx?' in flow.request.url:
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('newslist')
        for rs in newslist:
            data = rs.get('data')
            title = data.get('cardinfo').get('title')
            scheme = rs.get('scheme')
            url  = parse_scheme(scheme)
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            ctx.log.alert(title)
            try:
                collection = db['car_home_recommand']
                collection.insert_one(info)
                logger.warning('insert 成功！%s' % info)
            except Exception as err:
                logger.error('%s - %s' % (err, info))

    # 原创
    if 'orinews?' in flow.request.url:
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('newslist')
        for rs in newslist:
            data = rs.get('data')
            title = data.get('title')
            url = data.get('url')
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            # insert_mongo(info)
            try:
                collection = db['car_home_orinews']
                collection.insert_one(info)
                logger.warning('insert 成功！%s' % info)
            except Exception as err:
                logger.error('%s - %s' % (err, info))

    # https://chejiahao.app.autohome.com.cn/chejiahao_v2_1_8/newspf/NPNewsListIntelligence.json?a=2&pm=2&v=10.8.5&au=83f4ff6d6f3446e59c8cabddbc1680080b3cbd95&operation=1&pageSize=&bsdata=eyJSZW1haW5EcUxlbiI6MCwicHZvcmRpbmEiOjAsInB2VGltZSI6MTU5MDQxNjYyMX0%3D&deviceId=e1962bba_c20b_4d3f_a974_e8a5386c9860&netstate=5&gps=113.8980404853619%2C22.575505503912332&followUIds=&topInfoId=6169038&type=1&cityId=110100
    # 车家号
    # if flow.request.url.startswith('https://chejiahao.app.autohome.com.cn/chejiahao'):
    if ('chejiahao_v2_1_8/newspf/NPNewsListIntelligence.json?' in flow.request.url):
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('newslist')
        for rs in newslist:
            title = rs.get('title')
            url = 'http://chejiahao.m.autohome.com.cn/share/info/'+str(rs.get('newsid'))
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            # insert_mongo(info)
            try:
                collection = db['car_home_chejia']
                collection.insert_one(info)
                logger.warning('insert 成功！%s' % info)
            except Exception as err:
                logger.error('%s - %s' % (err, info))
    # 直播(暂时不行)
    if ('/live/GetFastNewsListV2' in flow.request.url):
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('fast_news').get('list')
        for rs in newslist:
            fast_news = rs.get('fast_news')
            title = rs.get('title')
            scheme = rs.get('scheme')
            roomid = scheme.split('&')[-2].split('=')[1]
            pvid = scheme.split('&')[-1].split('=')[1]
            url = 'https://live.autohome.com.cn/live/'+roomid+'/#pvareaid='+pvid
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            insert_mongo(info)

    # 小视频
    # https://news.app.autohome.com.cn/video_v10.0.0/news/smallvideorecommend?pm=2&lasttime=0&version=10.8.5&bi=1&useridvalue=7280ef4211be479e7012f943e42292c6&auth=83f4ff6d6f3446e59c8cabddbc1680080b3cbd95&deviceid=e1962bba_c20b_4d3f_a974_e8a5386c9860&operation=1&netstate=5&gps=113.8980404853619%2C22.575505503912332&bsdata=eyJSZW1haW5EcUxlbiI6MCwicHZvcmRpbmEiOjAsInB2VGltZSI6MTU5MDQyMDQ0M30%3D&pagesize=0&osversion=8.1.0&backdata=&tagid=0&tagname=&devicetype=2&cityid=110100
    if 'smallvideorecommend' in flow.request.url:
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('newslist')
        for rs in newslist:
            title = rs.get('data').get('title')
            url = rs.get('data').get('url')
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            insert_mongo(info)

    # 视频
    # https://103.75.152.210/video_v10.0.0/news/newvideoedit?pm=2&tagid=0&pageid=0&size=20&iscludrecv=0&devicetype=2
    if 'newvideoedit' in flow.request.url:
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('list')
        for rs in newslist:
            data = rs.get('data')
            title = data.get('title')
            url = data.get('url')
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            insert_mongo(info)

    # # 新能源
    # # https://news.app.autohome.com.cn/news_v10.0.0/news/rcm?pm=2&subjectids=&version=10.8.5&bi=1&devid=e1962bba_c20b_4d3f_a974_e8a5386c9860&op=1&net=5&gps=113.8980404853619%2C22.575505503912332&isonline=1&showfocusimg=1&bsdata=eyJSZW1haW5EcUxlbiI6MCwicHZvcmRpbmEiOjEsInB2VGltZSI6MTU5MDQxNjYyNX0%253D&pagesize=0&ratio=-1&restart=1&gaid=&idfa=&typeid=1&channelid=10100&os_version=8.1.0&rnversion=3.0.0&seriesid=0&useridvalue=7280ef4211be479e7012f943e42292c6&auth=83f4ff6d6f3446e59c8cabddbc1680080b3cbd95&devicetype=2&cityid=110100
    # if 'news/rcm?' in flow.request.url:
    #     text = flow.response.text
    #     data = json.loads(text)
    #     newslist = data.get('result').get('newslist')
    #     for rs in newslist:
    #         data = rs.get('data')
    #         title = data.get('title')
    #         mediatype = data.get('mediatype')
    #         id = data.get('id')
    #         time = data.get('updatetime')[0:6]
    #         if mediatype == 1:
    #             url = 'https://www.autohome.com.cn/news/'+str(time)+'/'+str(id)+'.html'
    #         if mediatype == 3:
    #             url = 'https://v.autohome.com.cn/v-'+str(id)+'.html'
    #         info = {
    #             'tag': '汽车之家',
    #             'title': title,
    #             'url': url,
    #             '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
    #         }
    #         ctx.log.alert(str(info))
    #         insert_mongo(info)

    # 行业
    # https://news.app.autohome.com.cn/news_v10.0.0/news/newindustry?pm=2&typeid=0&pageid=0&size=30&version=10.8.5
    if 'newindustry' in flow.request.url:
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('newslist')
        for rs in newslist:
            try:
                data = rs.get('data')
                title = data.get('title')
                mediatype = data.get('mediatype')
                id = data.get('id')
                time = data.get('updatetime')[0:6]
                if mediatype == 1:
                    url = 'https://www.autohome.com.cn/news/' + str(time) + '/' + str(id) + '.html'
                if mediatype == 3:
                    url = 'https://v.autohome.com.cn/v-' + str(id) + '.html'
            except:
                data = rs.get('data')
                title = data.get('title')
                id = data.get('id')
                time = data.get('updatetime')[0:6]
                url = 'https://www.autohome.com.cn/advice/' + time + '/' + str(id) + '.html#p1'
                info = {
                    'tag': '汽车之家',
                    'title': title,
                    'url': url,
                    '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
                }

            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            insert_mongo(info)

    # Young
    # https://young1.api.autohome.com.cn/api/young/getColumnDynamic?currentIndex=0&currentId=0&_appid=heicar.android&_timestamp=1590420959&_sign=07F93151864BDF72E506DF2672BE15D6
    if 'getColumnDynamic' in flow.request.url:
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('list')
        for rs in newslist:
            data = rs.get('data')
            title = rs.get('title')
            url = rs.get('targeturl')
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            insert_mongo(info)
    # Young
    # https://young1.api.autohome.com.cn/api/young/getColumnDynamic?currentIndex=0&currentId=0&_appid=heicar.android&_timestamp=1590420959&_sign=07F93151864BDF72E506DF2672BE15D6
    if 'young/yintelrecommend?' in flow.request.url:
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('feedlist')
        for rs in newslist:
            title = rs.get('title')
            url = rs.get('shareurl')
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            insert_mongo(info)

    # 口碑
    # https://103.75.152.210/autov9.13.0/AppHome/AppNewSmartHandler.ashx?pm=2&returnbanner=1&devicetype=android-Pixel&userid=188530069&deviceid=e1962bba_c20b_4d3f_a974_e8a5386c9860&operation=1&gps=22.575505503912332%2C113.8980404853619&appversion=10.8.5&bsdata=
    if 'AppNewSmartHandler' in flow.request.url:
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('AppHomeSmartItems')
        for rs in newslist:
            title = rs.get('Title')
            Objid = rs.get('Objid')
            SpecId = rs.get('SpecId')
            if(SpecId!=0):
                url = 'https://k.autohome.com.cn/spec/'+str(SpecId)+'/'
            else:
                url = 'https://v.m.autohome.com.cn/small/v-'+str(Objid)+'.html'
            # url = rs.get('UrlScheme')
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            insert_mongo(info)

    # 图片(可以获取图片url)和新能源板块的文章列表相同
    # https://103.75.152.210/news_v10.0.0/news/rcm?pm=2&subjectids=&version=10.8.5&bi=1&uid=188530069&devid=e1962bba_c20b_4d3f_a974_e8a5386c9860&op=0&net=5&gps=113.8980404853619,22.575505503912332&isonline=1&showfocusimg=0&bsdata=&auth=83f4ff6d6f3446e59c8cabddbc1680080b3cbd95&pagesize=30&ratio=-1&restart=0&gaid=&idfa=&typeid=0&channelid=10300&os_version=8.1.0&devicetype=2&cityid=110100
    if 'news/rcm' in flow.request.url:
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('newslist')
        for rs in newslist:
            data = rs.get('data')
            title = data.get('title')
            id = data.get('id')
            time = data.get('updatetime')[0:6]
            url = 'https://www.autohome.com.cn/advice/'+time+'/'+str(id)+'.html#p1'
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            insert_mongo(info)

    # 话题
    # 无法加载
    # 2020.10.16添加
    if ('news/newstopicrecommend?' in flow.request.url):
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('newslist')
        focusinglist = data.get('result').get('focusimglist')
        insertlist = data.get('result').get('insertlist')
        for news in newslist:
            title = news.get('data').get('title')
            datatime = news.get('data').get('updatetime')[0:6]
            id = news.get('data').get('id')
            url = 'https://www.autohome.com.cn/news/' + datatime + '/' + str(id) + '.html'
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            insert_mongo(info)
    # 论坛
    # https://103.75.152.210/club_v9.6.0/club/index/clubbusiness?pm=2&version=10.8.5&_timestamp=1590421384&motion=0&_sign=A9F37D1C8E8BE3A5582321DB9339F93F&t=2&cid=110100&model=1&deviceid=e1962bba_c20b_4d3f_a974_e8a5386c9860
    if 'clubbusiness' in flow.request.url:
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('uplist')
        for rs in newslist:
            title = rs.get('title')
            url = rs.get('schema')
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            insert_mongo(info)
    # 论坛
    # https://103.75.152.210/club_v9.6.0/club/index/clubbusiness?pm=2&version=10.8.5&_timestamp=1590421384&motion=0&_sign=A9F37D1C8E8BE3A5582321DB9339F93F&t=2&cid=110100&model=1&deviceid=e1962bba_c20b_4d3f_a974_e8a5386c9860
    if 'club/index/newdynamic?' in flow.request.url:
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('list')
        for rs in newslist:
            title = rs.get('data').get('title')
            topicid = rs.get('data').get('topicid')
            url = 'http://live.m.autohome.com.cn/live/'+str(topicid)
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            insert_mongo(info)
    # Young
    # https://103.75.153.2/api/young/getColumnDynamic?currentIndex=2&currentId=479&_appid=heicar.android&_timestamp=1590421516&_sign=FC22E565C5A6EAD11C42036259BFE859
    if 'getColumnDynamic' in flow.request.url:
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('list')
        for rs in newslist:
            title = rs.get('longtitle')
            url = rs.get('targeturl')
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            insert_mongo(info)
    # Young
    # https://103.75.153.2/api/young/getColumnDynamic?currentIndex=2&currentId=479&_appid=heicar.android&_timestamp=1590421516&_sign=FC22E565C5A6EAD11C42036259BFE859
    if 'young/yintelrecommend?' in flow.request.url:
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('feedlist')
        for rs in newslist:
            title = rs.get('title')
            url = rs.get('shareurl')
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            insert_mongo(info)
    # 微帖(是没有链接的)
    # https://103.75.153.2/api/clubtopic/getgambittopicslist?gambitId=0&pageIndex=1&pageSize=20&lastTopicId=87815258&_appid=&_version=V10.8.5&_nonce=e1962bba_c20b_4d3f_a974_e8a5386c98601590421475275&_timestamp=1590421627&_sign=D2C318E0CC808C3A3B274CC4A1C23543
    if 'getgambittopicslist' in flow.request.url:
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('list')
        for rs in newslist:
            title = rs.get('title')
            url = rs.get('url')
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            insert_mongo(info)

    # 直播
    # https://103.75.152.210/club_v9.6.0/club/livelist?pm=2&version=10.8.5&pageid=0&tageid=0&topids=0&pagesize=20
    if 'livelist' in flow.request.url:
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('list')
        for rs in newslist:
            title = rs.get('title')
            liveid = rs.get('liveid')
            url = 'http://live.m.autohome.com.cn/live/'+str(liveid)
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            insert_mongo(info)

    # 视频社区
    # https://103.75.152.210/community_v9.5.0/pic/forumvc/videos?pm=2&v=10.8.5&deviceid=e1962bba_c20b_4d3f_a974_e8a5386c9860&bsdata=&useridept=7280ef4211be479e7012f943e42292c6&auth=83f4ff6d6f3446e59c8cabddbc1680080b3cbd95&operation=0&devicetype=android.Pixel&netstate=0&gps=22.575505503912332%2C113.8980404853619&number=20
    if 'community' in flow.request.url:
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('list')
        for rs in newslist:
            data = rs.get('data')
            title = data.get('title')
            url = data.get('shareurl')
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            insert_mongo(info)

    # 自驾游（抓不到)
    # https://y.autohome.com.cn/api_app/api/open/contents/t_v10.2.5/list/all
    if 'contents' in flow.request.url:
        text = flow.response.text
        data = json.loads(text)
        newslist = data.get('result').get('travelList')
        for rs in newslist:
            data = rs.get('travelInfo')
            title = data.get('title')
            url = data.get('travelUrl')
            info = {
                'tag': '汽车之家',
                'title': title,
                'url': url,
                '_id': hashlib.md5(str(title).encode(encoding='UTF-8')).hexdigest()
            }
            ctx.log.alert(str(info))
            insert_mongo(info)