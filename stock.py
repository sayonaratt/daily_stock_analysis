import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

# =========== 只改这里：换成你的 Tushare Token ===========
ts.set_token("d76b529ceb9f76e240f499208f1c7ad1e9c86148b2e9086c53cadee2")
pro = ts.pro_api()


if __name__ == "__main__":
    # 1. 获取最近一个交易日的日线数据
    today = datetime.now()
    for i in range(5):
        trade_date = (today - timedelta(days=i)).strftime("%Y%m%d")
        try:
            df = pro.daily(trade_date=trade_date, fields="ts_code,close,vol")
            if not df.empty:
                print(f"✅ 成功获取 {trade_date} 数据，共 {len(df)} 只股票")
                break
        except Exception as e:
            print(f"❌ {trade_date} 获取失败: {e}")
            continue
    else:
        print("❌ 连续5天都没拿到数据，请检查Token")
        exit()

    # 2. 筛选成交量大于50000手的股票（可根据需要调整）
    high_volume = df[df["vol"] > 50000].copy()

    # 👇 直接在日志里打印全部结果，不用文件
    print("\n" + "="*60)
    print(f"📊 筛选结果：成交量>50000手的股票，共 {len(high_volume)} 只")
    print("="*60)
    # 用表格形式打印，复制到Excel就能用
    print(high_volume.to_string(index=False))
    print("="*60)
