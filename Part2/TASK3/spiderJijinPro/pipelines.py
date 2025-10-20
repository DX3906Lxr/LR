import pymysql

class JijinPipeline:
    def __init__(self):
        self.conn = pymysql.connect(
            host="localhost",
            user="root",
            password="xr123321",
            database="mydatabase",
            charset="utf8mb4"
        )
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        # 判断是基金净值数据还是基金基本信息（靠字段判断）
        if "buy_status" in item and "sell_status" in item:
            # 插入净值数据
            sql = """
                INSERT IGNORE INTO fund_nav_history 
                (fund_code, date, unit_nav, accumulated_nav, daily_growth_rate, buy_status, sell_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(sql, (
                item.get("fund_code"),
                item.get("date"),
                item.get("unit_nav"),
                item.get("accumulated_nav"),
                item.get("daily_growth_rate"),
                item.get("buy_status"),
                item.get("sell_status")
            ))
            self.conn.commit()
        else:
            # 如果你未来想保存基金基本信息，也可在此添加另一张表
            pass
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":
    p = JijinPipeline()
    print("数据库测试写入中...")
    p.cursor.execute("SHOW DATABASES;")
    for db in p.cursor.fetchall():
        print(db)
    p.conn.close()