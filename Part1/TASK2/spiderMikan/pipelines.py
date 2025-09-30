# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
class FanItemPipeline:
    def process_item(self, item, spider):
        item["fullpath"] = "/Users/DX3906/Desktop/工作室/凌睿/二轮/爬虫/spiderMikan/downloads/"+item["files"][0].get("path")
        return item


