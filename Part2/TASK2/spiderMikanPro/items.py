# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class TorrentItem(scrapy.Item):
    title = scrapy.Field()
    size = scrapy.Field()
    file_urls = scrapy.Field()
    file_paths = scrapy.Field()
    transform = scrapy.Field()

    original_filename = scrapy.Field()
    file_size_bytes = scrapy.Field()
    fansub_group = scrapy.Field()
    anime_title = scrapy.Field()
    resolution = scrapy.Field()
    encode_info = scrapy.Field()
    language = scrapy.Field()
    file_format = scrapy.Field()
    torrent_data = scrapy.Field()
    files = scrapy.Field()
    fullpath= scrapy.Field()
