# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

###########################
######	EM MOGODB #########
###########################
# import pymongo
#
#
# class PontofrioPipeline(object):
#     collection_name = 'computadores'
#
#     def __init__(self, mongo_uri, mongo_db):
#         self.mongo_uri = mongo_uri
#         self.mongo_db = mongo_db
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         return cls(
#             mongo_uri=crawler.settings.get('MONGODB_URL'),
#             mongo_db=crawler.settings.get('MONGODB_DB', 'defautlt-test')
#         )
#
#     def open_spider(self, spider):
#         self.client = pymongo.MongoClient(self.mongo_uri)
#         self.db = self.client[self.mongo_db]
#
#     def close_spider(self, spider):
#         self.client.close()
#
#     def process_item(self, item, spider):
#         self.db[self.collection_name].insert(dict(item))
#         return item
###########################

'''
	EM RETHINKDB
'''

import rethinkdb as r


class PontofrioPipeline(object):

    conn = None
    rethinkdb_settings = {}

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings

        rethinkdb_settings = settings.get('RETHINKDB', {})

        return cls(rethinkdb_settings)

    def __init__(self, rethinkdb_settings):
        self.rethinkdb_settings = rethinkdb_settings

    def open_spider(self, spider):
        if self.rethinkdb_settings:
            self.table_name = self.rethinkdb_settings.pop('table_name')
            self.db_name = self.rethinkdb_settings['db']
            self.conn = r.connect(**self.rethinkdb_settings)
            table_list = r.db(self.db_name).table_list().run(
                self.conn
            )
            if self.table_name not in table_list:
                r.db(self.db_name).table_create(self.table_name).run(self.conn)

    def close_spider(self, spider):
        if self.conn:
            self.conn.close()

    def process_item(self, item, spider):
        if self.conn:
            r.table(self.table_name).insert(item).run(self.conn)
        return item
