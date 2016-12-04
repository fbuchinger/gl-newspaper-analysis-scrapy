# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class DmozItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    desc = scrapy.Field()

def serialize_csv(value):
    value = "".join(value.split(","))
    return "".join(value.splitlines())
    
class NewspaperItem(scrapy.Item):
    requested_url = scrapy.Field()
    snapshot_date = scrapy.Field()
    textTopFontColor = scrapy.Field()
    textTopFont = scrapy.Field()
    textTopFontSize = scrapy.Field()
    textUniqueFontSizeCount = scrapy.Field()
    textUniqueFontColorCount = scrapy.Field()
    textUniqueFontCount = scrapy.Field()
    textVisibleCharCount = scrapy.Field()
    textTopFontStyle = scrapy.Field()
    ISOTimeStamp = scrapy.Field()
    version = scrapy.Field()
    textFirst1000Chars = scrapy.Field(serializer=serialize_csv)