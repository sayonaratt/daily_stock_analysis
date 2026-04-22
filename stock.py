import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

# =========== 只改这里：换成你的 Tushare Token ===========
ts.set_token("d76b529ceb9f76e240f499208f1c7ad1e9c86148b2e9086c53cadee2")
pro = ts.pro_api()


def get_latest_trade_data():
    """自动获取最近一个交易日的行情数据，用免费接口自己算换手率"""
    today = datetime.now()
    trade_date = today.strftime("%Y%m%d")

    # 往前找最多5天，直到拿到数据
    for i in range(5):
        try:
            # 用免费的 daily 接口获取日线数据
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


def get_stock_basics():
    """获取股票总股本数据（用于计算换手率）"""
    try:
        # 获取所有A股的基本信息
        df = pro.stock_basic(
            exchange='',
            list_status='L',
            fields='ts_code,total_share'
        )
        print(f"✅ 成功获取到股票基础信息，共 {len(df)} 只股票")
        return df
    except Exception as e:
        print(f"❌ 获取股票基础信息失败: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    # 1. 获取最新交易日行情数据
    stock_df, latest_trade_date = get_latest_trade_data()

    if stock_df.empty or latest_trade_date is None:
        print("❌ 行情数据为空，无法继续筛选")
        exit(1)

    # 2. 获取总股本数据，用于计算换手率
    basics_df = get_stock_basics()
    if basics_df.empty:
        print("❌ 股票基础信息为空，无法计算换手率")
        exit(1)

    # 3. 合并数据，计算换手率
    # 单位说明：vol 是手（1手=100股），total_share 是万股
    # 换手率 = (成交量股数 / 总股本股数) * 100%
    merged_df = pd.merge(stock_df, basics_df, on='ts_code', how='left')
    
    # 计算换手率
    merged_df['turnover_rate'] = (merged_df['vol'] * 100) / (merged_df['total_share'] * 10000) * 100

    # 4. 筛选换手率大于5%的股票
    high_turnover = merged_df[merged_df["turnover_rate"] > 5].copy()
    print(f"\n📊 换手率大于5%的股票共 {len(high_turnover)} 只：")
    print(high_turnover[["ts_code", "close", "turnover_rate"]].to_string(index=False))

    # 5. 保存结果到 CSV 文件
    high_turnover.to_csv(f"high_turnover_stocks_{latest_trade_date}.csv", index=False, encoding="utf-8-sig")
    print(f"\n✅ 筛选结果已保存到文件：high_turnover_stocks_{latest_trade_date}.csv")
