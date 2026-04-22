import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

# =========== 只改这里：换成你的 Tushare Token ===========
ts.set_token("d76b529ceb9f76e240f499208f1c7ad1e9c86148b2e9086c53cadee2")
pro = ts.pro_api()


def get_latest_trade_data():
    """自动获取最近一个交易日的行情数据（用 daily_basic 接口获取换手率）"""
    today = datetime.now()
    trade_date = today.strftime("%Y%m%d")

    # 往前找最多5天，直到拿到数据
    for i in range(5):
        try:
            # 关键修复：使用 daily_basic 接口，它才有 turnover_rate 字段
            df = pro.daily_basic(
                trade_date=trade_date,
                fields="ts_code,trade_date,turnover_rate,close,volume"
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

    print("❌ 连续5天都未获取到数据，请检查 Tushare Token 和权限")
    return pd.DataFrame(), None


if __name__ == "__main__":
    # 1. 获取最新交易日数据
    stock_df, latest_trade_date = get_latest_trade_data()

    if stock_df.empty or latest_trade_date is None:
        print("❌ 数据为空，无法继续筛选")
        exit(1)

    # 2. 检查 turnover_rate 列是否存在，避免 KeyError
    if "turnover_rate" not in stock_df.columns:
        print("❌ 数据中没有 turnover_rate 列，请检查接口和字段配置")
        print("当前数据列名：", stock_df.columns.tolist())
        exit(1)

    # 3. 筛选换手率大于5%的股票
    high_turnover = stock_df[stock_df["turnover_rate"] > 5].copy()
    print(f"\n📊 换手率大于5%的股票共 {len(high_turnover)} 只：")
    print(high_turnover[["ts_code", "turnover_rate", "close"]].to_string(index=False))

    # 4. 可选：保存结果到 CSV 文件，方便后续使用
    high_turnover.to_csv(f"high_turnover_stocks_{latest_trade_date}.csv", index=False, encoding="utf-8-sig")
    print(f"\n✅ 筛选结果已保存到文件：high_turnover_stocks_{latest_trade_date}.csv")
