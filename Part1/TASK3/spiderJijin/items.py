# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JijinItem(scrapy.Item):
    fund_code = scrapy.Field()
    fund_name = scrapy.Field()
    date = scrapy.Field()
    unit_nav = scrapy.Field()
    accumulated_nav = scrapy.Field()
    daily_growth_rate = scrapy.Field()
    return_1w = scrapy.Field()
    return_1m = scrapy.Field()
    return_3m = scrapy.Field()
    return_6m = scrapy.Field()
    return_1y = scrapy.Field()
    return_2y = scrapy.Field()
    return_3y = scrapy.Field()
    return_ytd = scrapy.Field()
    return_since_inception = scrapy.Field()
    fee_rate = scrapy.Field()
    pass
