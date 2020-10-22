'''
自动获取微信公众号的名称和数量（多线程工作准备中）
'''

import uiautomator2 as u2
from uiautomator2 import Direction
import time
import cv2
import redis
import hashlib

#连接数据库db0
r = redis.Redis(host='127.0.0.1', port=6379,db=0)

# 使用连接池连接数据库。这样就可以实现多个Redis实例共享一个连接池
pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
#创建一个redis实例
r = redis.Redis(connection_pool=pool)


serial = '1e805508'
try:
    d = u2.connect(serial)
except Exception:
    print("usb连接已断开")
    exit(0)
d.app_stop('com.tencent.mm')
d.app_start('com.tencent.mm')
time.sleep(3)
d(text='通讯录').click()
d(text='公众号').click()
name = set()
num = 0
while (not d.xpath('//*[@resource-id="com.tencent.mm:id/d2t"]/android.widget.FrameLayout[1]').exists):
    time.sleep(2)
    text = d.xpath('com.tencent.mm:id/a71').all()
    for i in text:
        if(i not in name):
            print(i.text)
        name.add(i)
        r.sadd('wechat',str(i.text))

    d.swipe(0.5, 0.8, 0.5, 0.2)

#最后一页的内容可能遗漏需要在补充一次
text = d.xpath('com.tencent.mm:id/a71').all()
for i in text:
    if(i not in name):
        print(i.text)
    name.add(i)
    r.sadd('wechat',str(i.text))
print("一共关注了"+str(len(name))+"个公众号")