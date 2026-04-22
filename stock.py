import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

# =========== 只改这里：换成你的 Tushare Token ===========
ts.set_token("d76b529ceb9f76e240f499208f1c7ad1e9c86148b2e9086c53cadee2")
pro = ts.pro_api()


def get_latest_trade_data():
    """获取最近一个交易日的免费日线数据"""
    today = datetime.now()
    trade_date = today.strftime("%Y%m%d")

    # 往前找最多5天，直到拿到数据
    for i in range(5):
        try:
            df = pro.daily(
                trade_date=trade_date,
                fields="ts_code,trade_date,open,high,low,close,vol"
            )
            if not df.empty:
                print(f"✅ 成功获取到【{trade_date}】的行情数据，共 {len(df)} 只股票")
                return df, trade_date
        except Exception as e:
            print(f"❌ 尝试获取 {trade_date} 数据失败: {e}")

        today -= timedelta(days=1)
        trade_date = today.strftime("%Y%m%d")

    print("❌ 连续5天都未获取到数据，请检查 Tushare Token")
    return pd.DataFrame(), None


if __name__ == "__main__":
    # 1. 获取最新交易日行情数据
    stock_df, latest_trade_date = get_latest_trade_data()

    if stock_df.empty or latest_trade_date is None:
        print("❌ 行情数据为空，无法继续筛选")
        exit(1)

    # 2. 筛选成交量大于50000手的股票（先放宽条件，确保有结果）
    high_volume = stock_df[stock_df["vol"] > 50000].copy()

    # 👇 强制打印，确保日志里能看到结果
    print("\n" + "="*50)
    print(f"📊 筛选结果：成交量大于50000手的股票，共 {len(high_volume)} 只")
    print("="*50)
    # 只打印关键列，避免被截断
    print(high_volume[["ts_code", "close", "vol"]].to_string(index=False))
    print("="*50 + "\n")

    # 3. 保存结果到 CSV 文件
    file_name = f"high_volume_stocks_{latest_trade_date}.csv"
    high_volume.to_csv(file_name, index=False, encoding="utf-8-sig")
    print(f"✅ 结果已保存到文件：{file_name}")
