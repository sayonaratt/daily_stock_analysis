import tushare as ts
import pandas as pd
from datetime import datetime

# 把这里换成你自己的 tushare token
ts.set_token("72e9dd8b12ea82becd9b67bc307d0e9db7248068bf47cd6ec0c89fb3")
pro = ts.pro_api()

# 获取今天日期
today = datetime.now().strftime("%Y%m%d")

try:
    # 获取全部股票日线
    df = pro.daily(trade_date=today, fields="ts_code,symbol,name,turnover_rate")
    
    # 过滤换手率 >5%
    df = df[df["turnover_rate"] > 5].copy()

    res = []

    # 计算KDJ并筛选
    for _, row in df.iterrows():
        try:
            kdata = ts.pro_bar(ts_code=row["ts_code"], adj="qfq", ma=9, limit=30)
            if kdata is None or len(kdata) < 20:
                continue

            kdata = kdata.iloc[::-1].reset_index(drop=True)

            low9 = kdata["low"].rolling(9).min()
            high9 = kdata["high"].rolling(9).max()
            kdata["rsv"] = (kdata["close"] - low9) / (high9 - low9) * 100
            kdata["K"] = kdata["rsv"].ewm(span=3, adjust=False).mean()
            kdata["D"] = kdata["K"].ewm(span=3, adjust=False).mean()

            k = round(kdata["K"].iloc[-1], 2)
            d = round(kdata["D"].iloc[-1], 2)

            if k < 50 and d < 50:
                res.append({
                    "代码": row["symbol"],
                    "名称": row["name"],
                    "换手率": round(row["turnover_rate"], 2),
                    "K值": k,
                    "D值": d
                })
        except:
            continue

    # 保存结果
    result = pd.DataFrame(res)
    result.to_csv("今日选股结果.csv", index=False, encoding="utf-8-sig")
    print("执行完成！")
    print(result)

except Exception as e:
    print("未获取到今日行情或非交易日")
