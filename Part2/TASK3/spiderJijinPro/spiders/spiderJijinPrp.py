import scrapy
import re
import json
from spiderJijinPro.items import JijinProItem, FundNavItem


class JijinSpiderPro(scrapy.Spider):
    name = "JijinPro"
    allowed_domains = ["fund.eastmoney.com", "api.fund.eastmoney.com"]

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

        for page in range(1, 21):
            params["pi"] = page
            query = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{query}"
            yield scrapy.Request(
                url=full_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) "
                                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/92.0.4515.159 Safari/537.36",
                    "Referer": "https://fund.eastmoney.com/fund.html"
                }
            )

    def parse(self, response):
        text = response.text
        m = re.search(r"\[(.*)\]", text)
        if not m:
            return
        rows = m.group(1).split('","')
        for r in rows:
            cols = r.replace('"', "").split(",")
            del cols[2]

            item = JijinProItem()
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
            item["fee_rate"] = cols[18] if cols[18] else "0.00%"
            yield item


            fund_code = item["fund_code"]
            api_url = (
                f"http://api.fund.eastmoney.com/f10/lsjz?"
                f"fundCode={fund_code}&pageIndex=1&pageSize=20"
            )
            yield scrapy.Request(
                url=api_url,
                callback=self.parse_history_api,
                meta={"fund_code": fund_code, "page": 1},
                headers={
                    "Referer": f"http://fundf10.eastmoney.com/jjjz_{fund_code}.html",
                    "User-Agent": "Mozilla/5.0"
                }
            )

    def parse_history_api(self, response):
        fund_code = response.meta["fund_code"]
        page = response.meta["page"]

        data = json.loads(response.text)

        records = data.get("Data", {}).get("LSJZList", [])
        print(f" {fund_code} 第 {page} 页，共 {len(records)} 条")

        for record in records:
            nav_item = FundNavItem()
            nav_item["fund_code"] = fund_code
            nav_item["date"] = record.get("FSRQ")
            nav_item["unit_nav"] = record.get("DWJZ")
            nav_item["accumulated_nav"] = record.get("LJJZ")
            nav_item["daily_growth_rate"] = record.get("JZZZL")
            nav_item["buy_status"] = record.get("SGZT")
            nav_item["sell_status"] = record.get("SHZT")
            yield nav_item

        if len(records) == 20:
            next_page = page + 1
            next_url = (
                f"http://api.fund.eastmoney.com/f10/lsjz?"
                f"fundCode={fund_code}&pageIndex={next_page}&pageSize=20"
            )
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_history_api,
                meta={"fund_code": fund_code, "page": next_page},
                headers={
                    "Referer": f"http://fundf10.eastmoney.com/jjjz_{fund_code}.html",
                    "User-Agent": "Mozilla/5.0"
                }
            )
