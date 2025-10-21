import pandas as pd
import numpy as np
import pymysql

# ==========================
# 1. 数据库连接配置
# ==========================
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="xr123321",
    database="mydatabase",
    charset="utf8mb4"
)
cursor = conn.cursor()

query = """
WITH top_funds AS (
    SELECT DISTINCT fund_code
    FROM fund_nav_history
    LIMIT 30
)
SELECT fund_code, date, unit_nav, accumulated_nav, daily_growth_rate, buy_status, sell_status
FROM fund_nav_history
WHERE fund_code IN (SELECT fund_code FROM top_funds)
"""
cursor.execute(query)
rows = cursor.fetchall()


df = pd.DataFrame(rows, columns=[
    'fund_code', 'date', 'unit_nav', 'accumulated_nav',
    'daily_growth_rate', 'buy_status', 'sell_status'
])
cursor.close()
conn.close()

print(f"✅ 数据加载成功，共 {df.shape[0]} 条记录，包含 {df['fund_code'].nunique()} 只基金。")
print(df.head())

# 数据清洗
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date'])  # 删除无效日期
df = df.sort_values(['fund_code', 'date']).reset_index(drop=True)
df = df.drop_duplicates(subset=['fund_code', 'date'])

df['daily_growth_rate'] = (
        df['daily_growth_rate']
        .astype(str)
        .str.replace('%', '', regex=False)
        .replace('', np.nan)
        .astype(float) / 100
)

for col in ['unit_nav', 'accumulated_nav']:

    df[col] = pd.to_numeric(df[col], errors='coerce')
    df.loc[(df[col] <= 0) | (df[col] > 1000), col] = np.nan
    df[col] = df.groupby('fund_code')[col].transform(lambda x: x.ffill().bfill())


df.loc[df['daily_growth_rate'].abs() > 0.2, 'daily_growth_rate'] = np.nan
df['daily_growth_rate'] = df.groupby('fund_code')['daily_growth_rate'].transform(lambda x: x.ffill().bfill())

df['buy_status'] = df['buy_status'].fillna('未知')
df['sell_status'] = df['sell_status'].fillna('未知')

df['buy_status'] = (df['buy_status'] == '开放').astype(int)
df['sell_status'] = (df['sell_status'] == '开放').astype(int)


#特征工程
def compute_features(group):
    g = group.copy().sort_values('date')

    #收益率
    g['return'] = g['unit_nav'].pct_change()


    #MACD
    ema_12 = g['unit_nav'].ewm(span=12, adjust=False).mean()
    ema_26 = g['unit_nav'].ewm(span=26, adjust=False).mean()
    g['macd'] = ema_12 - ema_26
    g['macd_signal'] = g['macd'].ewm(span=9, adjust=False).mean()
    g['macd_hist'] = g['macd'] - g['macd_signal']

    #RSI
    delta = g['unit_nav'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    RS = gain / (loss + 1e-9)
    g['rsi'] = 100 - (100 / (1 + RS))

    #移动平均线
    g['ma_5'] = g['unit_nav'].rolling(window=5).mean()
    g['ma_20'] = g['unit_nav'].rolling(window=20).mean()

    #滚动收益率
    g['rolling_return_5'] = g['unit_nav'].pct_change(periods=5)
    g['rolling_return_20'] = g['unit_nav'].pct_change(periods=20)

    #滚动波动率
    g['rolling_vol_5'] = g['return'].rolling(5).std()
    g['rolling_vol_20'] = g['return'].rolling(20).std()

    #时间特征
    g['weekday'] = g['date'].dt.weekday
    g['month'] = g['date'].dt.month
    g['quarter'] = g['date'].dt.quarter

    return g

df_feat = df.groupby('fund_code', group_keys=False).apply(compute_features)

#缺失值处理
df_feat = df_feat.ffill().bfill()
df_feat = df_feat.dropna(subset=['unit_nav']).reset_index(drop=True)


#保存为 CSV
output_path = 'fund_features_full.csv'
df_feat.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"\n✅ 特征工程完成，共 {df_feat.shape[0]} 条记录，已保存至 {output_path}")
print("✅ 特征列包括：", list(df_feat.columns))
