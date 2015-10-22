# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# https://api.mongodb.org/python/current/tutorial.html

import scrapy
import logging
import pymongo


class SaveToMongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db, mongo_collection_name):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection_name = mongo_collection_name

    @classmethod
    def from_crawler(cls, crawler):
        assert crawler.settings['mongo_collection_name']
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items'),
            mongo_collection_name=crawler.settings['mongo_collection_name']
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

        self.db[self.mongo_collection_name].create_index(
            [('url', pymongo.ASCENDING)],
            unique=True
        )

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        try:
            self.db[self.mongo_collection_name].insert(dict(item))
        except pymongo.errors.DuplicateKeyError:
            raise scrapy.exceptions.DropItem(
                'Duplicate URL: {}'.format(item['url'])
            )
        return item

