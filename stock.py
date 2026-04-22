import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

# =========== 只改这里：换成你的 Tushare Token ===========
ts.set_token("d76b529ceb9f76e240f499208f1c7ad1e9c86148b2e9086c53cadee2")
pro = ts.pro_api()


def get_latest_trade_data():
    """获取最近一个交易日的免费日线数据，只筛选高成交量股票"""
    today = datetime.now()
    trade_date = today.strftime("%Y%m%d")

    # 往前找最多5天，直到拿到数据
    for i in range(5):
        try:
            # 只用完全免费的 daily 接口，不依赖任何特殊权限
            df = pro.daily(
                trade_date=trade_date,
                fields="ts_code,trade_date,open,high,low,close,vol"
            )
            if not df.empty:
                print(f"✅ 成功获取到【{trade_date}】的行情数据，共 {len(df)} 只股票")
                print("当前数据列名：", df.columns.tolist())
                return df, trade_date
        except Exception as e:
            print(f"❌ 尝试获取 {trade_date} 数据失败: {e}")

        # 往前推一天
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

    # 2. 直接用成交量vol替代换手率筛选（vol单位：手，1手=100股）
    # 这里设置筛选条件：成交量大于100000手（即1000万股），可以根据需要调整
    high_volume = stock_df[stock_df["vol"] > 100000].copy()
    print(f"\n📊 成交量大于100000手的股票共 {len(high_volume)} 只：")
    print(high_volume[["ts_code", "close", "vol"]].to_string(index=False))

    # 3. 保存结果到 CSV 文件
    high_volume.to_csv(f"high_volume_stocks_{latest_trade_date}.csv", index=False, encoding="utf-8-sig")
    print(f"\n✅ 筛选结果已保存到文件：high_volume_stocks_{latest_trade_date}.csv")
