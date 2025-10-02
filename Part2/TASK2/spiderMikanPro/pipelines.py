# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os

import pymysql
import re
from datetime import datetime

class TorrentPipeline:
    def __init__(self):
        self.conn = pymysql.connect(
            host="localhost",
            user="root",
            password="xr123321",
            database="mydatabase",
            charset="utf8mb4"
        )
        self.cursor = self.conn.cursor()

        self.pattern = re.compile(r"""
            (?P<fansub_group>\[.*?\]|【.*?】)?                    
            \s*
            (?P<anime_title>[\u4e00-\u9fff\u3040-\u30ffA-Za-z·\-—_]+)
        """, re.VERBOSE | re.IGNORECASE)

    def process_item(self, item, spider):

        original_filename = item.get("title", "未知文件名")

        size_str = item.get("size", "0").upper()
        multiplier = 1
        if "MB" in size_str:
            multiplier = 1024 * 1024
            size_val = float(size_str.replace("MB", "").strip())
        elif "GB" in size_str:
            multiplier = 1024 * 1024 * 1024
            size_val = float(size_str.replace("GB", "").strip())
        else:
            size_val = 0
        file_size_bytes = int(size_val * multiplier)

        m = self.pattern.search(original_filename)
        data = m.groupdict()

        fansub_group = item["transform"] or "UNK"
        anime_title = data.get("anime_title") or "UNK"

        resolution = re.search("1080|720", original_filename)
        if not resolution:
            resolution = "<UNK>"
        else:
            resolution = resolution.group()

        encode_info = re.search("x265|x264|HEVC|AVC", original_filename)
        if not encode_info:
            encode_info = "<UNK>"
        else:
            encode_info = encode_info.group()

        language = re.search("简|繁|日", original_filename)
        if not language:
            language = "<UNK>"
        else:
            language = language.group()

        file_format = re.search("MP4|MKV", original_filename)
        if not file_format:
            file_format = "<UNK>"
        else:
            file_format = file_format.group()

        torrent_data = b""
        if "files" in item and item["files"]:
            file_path = "/Users/DX3906/Desktop/工作室/凌睿/二轮/爬虫/spiderMikanPro/downloads/" + item["files"][0].get("path")
            with open(file_path, "rb") as f:
                torrent_data = f.read()

        sql = """
        INSERT INTO torrent_files 
        (original_filename, file_size_bytes, fansub_group, anime_title,
          resolution, encode_info,
         language, file_format, torrent_data,last_access)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        self.cursor.execute(sql, (
            original_filename,
            file_size_bytes,
            fansub_group,
            anime_title,
            resolution,
            encode_info,
            language,
            file_format,
            torrent_data,
            datetime.now(),
        ))
        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.conn.close()
