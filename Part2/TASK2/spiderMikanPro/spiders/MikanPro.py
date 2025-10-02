import scrapy
from scrapy import Selector, Request
from spiderMikanPro.items import TorrentItem

class MikanSpider(scrapy.Spider):
    name = "MikanPro"
    allowed_domains = ["mikanani.kas.pub"]

    def start_requests(self):

        for page in range(0,50):
            yield Request(url=f"https://mikanani.kas.pub/Home/Classic/{page}")

    def parse(self, response):
        sel = Selector(response)
        list_items = sel.css("#sk-body > table > tbody > tr")

        for list_item in list_items:
            item = TorrentItem()
            item["title"] = list_item.css("td:nth-child(3) a::text").get()
            item["transform"] = list_item.css("td:nth-child(2) a::text").extract_first()
            if not TorrentItem["transform"]:
                item["transform"] = list_item.css("td:nth-child(2)::text").extract_first()

            item["size"] = list_item.css("td:nth-child(4)::text").get()
            torrent_url = list_item.css("td:nth-child(5) a::attr(href)").get()
            if torrent_url:
                item["file_urls"] = [response.urljoin(torrent_url)]
            yield item
