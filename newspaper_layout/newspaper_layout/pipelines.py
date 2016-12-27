# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime
from scrapy.exceptions import DropItem

class NewspaperLayoutPipeline(object):
    def process_item(self, item, spider):
        if item.has_key('error'):
            raise DropItem("Error capturing item %s" % item)
        else:
            #try to set the snapshot date
            try:
                url_parts = item["requested_url"].split("/")
                snapshot_date = datetime.strptime(url_parts[4], '%Y%m%d%H%M%S')
                item['snapshot_date'] = str(snapshot_date)
            except:
                pass

            item['newspaper'] = 'unknown'
            newspapers = spider.custom_settings['NEWSPAPERS']
            for paper, paper_url in newspapers.items():
                if paper_url in item['requested_url']:
                    item['newspaper'] = paper

            first_1k_chars = item['textFirst1000Chars'];
            first_1k_chars = "".join(first_1k_chars.split(","))
            item['textFirst1000Chars'] = "".join(first_1k_chars.split());

            return item

