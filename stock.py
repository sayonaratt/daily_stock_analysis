import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

# =========== 只改这里：换成你的 Tushare Token ===========
ts.set_token("d76b529ceb9f76e240f499208f1c7ad1e9c86148b2e9086c53cadee2")
pro = ts.pro_api()


if __name__ == "__main__":
    # 1. 获取最近一个交易日的日线数据
    today = datetime.now()
    df = pd.DataFrame()
    trade_date = None

    # 往前找最多5天，直到拿到数据
    for i in range(5):
        temp_date = (today - timedelta(days=i)).strftime("%Y%m%d")
        try:
            temp_df = pro.daily(
                trade_date=temp_date,
                fields="ts_code,close,vol"
            )
            if not temp_df.empty:
                df = temp_df
                trade_date = temp_date
                print(f"✅ 成功获取到【{trade_date}】的行情数据，共 {len(df)} 只股票")
                break
        except Exception as e:
            print(f"❌ 尝试获取 {temp_date} 数据失败: {e}")
            continue
    else:
        print("❌ 连续5天都未获取到数据，请检查 Tushare Token")
        exit(1)

    # 2. 放宽筛选条件，确保一定有结果
    # 先筛出成交量大于10000手（100万股）的股票，这个条件几乎每天都有结果
    high_volume = df[df["vol"] > 10000].copy()

    # 👇 直接在日志里打印全部结果，用框线标出来，一眼就能找到
    print("\n" + "="*60)
    print(f"📊 筛选结果：成交量大于10000手的股票，共 {len(high_volume)} 只")
    print("="*60)
    # 打印表格，格式整齐，复制到Excel就能用
    print(high_volume.to_string(index=False))
    print("="*60)
