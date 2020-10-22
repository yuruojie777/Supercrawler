import pymongo
from pymongo import MongoClient

# 连接数据库
client = MongoClient('mongodb://localhost:27017/')
db = client['amazon']
dir_set = db.amazon_dir_info
computer_set = db.amazon_computer_info

# for data in dir_set.find():
#     print(data['good_type'],data['good_url'])

ebook_set = db.amazon_ebook_info
ebook_set.delete_many({})