import scrapy
import re
from spiderJijin.items import JijinItem

class JijinSpider(scrapy.Spider):
    name = "Jijin"
    allowed_domains = ["fund.eastmoney.com"]

    def start_requests(self):
        url = "https://fund.eastmoney.com/data/rankhandler.aspx"
        params = {
            "op": "ph",
            "dt": "kf",
            "ft": "all",
            "sc": "1nzf",
            "st": "desc",
            "pi": 1,
            "pn": 50,
            "dx": 1,
            "v": "abcdef123456"
        }
        for page in range(1, 101):
            params["pi"] = page
            query = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{query}"
            yield scrapy.Request(
                url=full_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
                    "Referer": "https://fund.eastmoney.com/fund.html"
                }
            )

    def parse(self, response):
        text = response.text
        m = re.search(r"\[(.*)\]", text)
        if m:
            rows = m.group(1).split('","')
            for r in rows:
                cols = r.replace('"', "").split(",")
                del cols[2]
               # print (cols)
                item = JijinItem()
                item["fund_code"] = cols[0]
                item["fund_name"] = cols[1]
                item["date"] = cols[2]
                item["unit_nav"] = cols[3]
                item["accumulated_nav"] = cols[4]
                item["daily_growth_rate"] = cols[5]
                item["return_1w"] = cols[6]
                item["return_1m"] = cols[7]
                item["return_3m"] = cols[8]
                item["return_6m"] = cols[9]
                item["return_1y"] = cols[10]
                item["return_2y"] = cols[11]
                item["return_3y"] = cols[12]
                item["return_ytd"] = cols[13]
                item["return_since_inception"] = cols[14]
                item["fee_rate"] = cols[18]
                if not item["fee_rate"]:
                    item["fee_rate"] = "0.00%"
                yield item
