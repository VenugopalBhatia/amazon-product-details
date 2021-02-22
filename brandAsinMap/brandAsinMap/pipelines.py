# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo





class BrandasinmapPipeline(object):
    
    def __init__(self,mongo_host,mongo_port,mongo_db,collection):
        self.mongo_host = mongo_host
        self.mongo_port = mongo_port
        self.mongo_db = mongo_db
        self.collection = collection
        
    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            mongo_host = crawler.settings.get("MONGODB_SERVER"),
            mongo_port = crawler.settings.get("MONGODB_PORT"),
            mongo_db = crawler.settings.get("MONGODB_DB"),
            collection = crawler.settings.get("MONGODB_COLLECTION")
        )
    
    def open_spider(self,spider):
        self.client = pymongo.MongoClient(self.mongo_host,self.mongo_port)
        self.db = self.client[self.mongo_db]
        self.connection = self.db[self.collection]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.connection.insert(dict(item))
        return item
                
