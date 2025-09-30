# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FanItem(scrapy.Item):
    title = scrapy.Field()
    size = scrapy.Field()
    magnet = scrapy.Field()
    transform = scrapy.Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()
    fullpath = scrapy.Field()