# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from collections import OrderedDict

class DmozItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    desc = scrapy.Field()

def serialize_csv(value):
    value = "".join(value.split(","))
    return "".join(value.splitlines())

def keylist_by_value(dict):
    o = OrderedDict(sorted(dict.items(), key=lambda t: t[0]))
    return "|".join(dict.keys())
    
class NewspaperItem(scrapy.Item):
    requested_url = scrapy.Field()
    snapshot_date = scrapy.Field()
    """textTopFontColor = scrapy.Field()
    textTopFont = scrapy.Field()
    textTopFontSize = scrapy.Field()
    textUniqueFontSizeCount = scrapy.Field()
    textUniqueFontColorCount = scrapy.Field()
    textUniqueFontCount = scrapy.Field()
    textVisibleCharCount = scrapy.Field()
    textTopFontStyle = scrapy.Field()
    ISOTimeStamp = scrapy.Field()
    version = scrapy.Field()
    textUniqueFonts = scrapy.Field(serializer=keylist_by_value)
    textFirst1000Chars = scrapy.Field(serializer=serialize_csv)"""

    textVisibleCharCount = scrapy.Field()
    textUniqueFonts = scrapy.Field()
    textUniqueFontCount = scrapy.Field()
    textFontList = scrapy.Field()
    textTopFont = scrapy.Field()
    textAverageRelativeLineHeight = scrapy.Field()
    textUniqueFontStyles = scrapy.Field()
    textUniqueFontStyleCount = scrapy.Field()
    textTopFontStyle = scrapy.Field()
    textUniqueFontSizes = scrapy.Field()
    textUniqueFontSizeCount = scrapy.Field()
    textTopFontSize = scrapy.Field()
    textAverageFontSize = scrapy.Field()
    textUniqueFontColors = scrapy.Field()
    textUniqueFontColorCount = scrapy.Field()
    textTopFontColor = scrapy.Field(serializer=keylist_by_value)
    textFirst1000Chars = scrapy.Field(serializer=serialize_csv)