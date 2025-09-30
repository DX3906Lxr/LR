import scrapy
from scrapy import Selector, Request
import time
import logging
from spiderMikan.items import FanItem

class MikanSpider(scrapy.Spider):
    name = "Mikan"
    allowed_domains = ["mikanani.kas.pub"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = time.time()
        self.req_count = 0

    def start_requests(self):
        for page in range(100):
            yield Request(url=f"https://mikanani.kas.pub/Home/Classic/{page}")

    def parse(self, response):
        self.req_count += 1  # 请求数+1
        sel = Selector(response)
        list_items = sel.css("#sk-body > table > tbody > tr")
        for list_item in list_items:
            fan_item = FanItem()
            fan_item["title"] = list_item.css("td:nth-child(3) a::text").extract_first()
            fan_item["size"] = list_item.css("td:nth-child(4)::text").extract_first()
            fan_item["magnet"] = list_item.css("td:nth-child(3) a.js-magnet::attr(data-clipboard-text)").extract_first()
            torrent_url = list_item.css("td:nth-child(5) a::attr(href)").extract_first()
            fan_item["file_urls"] = [response.urljoin(torrent_url)]
            fan_item["transform"] = list_item.css("td:nth-child(2) a::text").extract_first()
            if not fan_item["transform"]:
                fan_item["transform"] = list_item.css("td:nth-child(2)::text").extract_first()
            yield fan_item

    def closed(self, reason):
        elapsed = time.time() - self.start_time
        rps = self.req_count / elapsed
        logging.info(f"RPS={rps:.2f}")
