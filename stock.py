import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

# ========== 只改这里：换成你的 Tushare Token ==========
ts.set_token("d76b529ceb9f76e240f499208f1c7ad1e9c86148b2e9086c53cadee2")
pro = ts.pro_api()

def get_latest_trade_data():
    """自动获取最近一个交易日的行情数据"""
    today = datetime.now()
    trade_date = today.strftime("%Y%m%d")

    # 往前找最多5天，直到拿到数据
    for i in range(5):
        try:
            # 关键修复：fields 里加上 turnover_rate
            df = pro.daily(
                trade_date=trade_date,
                fields="ts_code,symbol,name,turnover_rate"
            )
            if not df.empty:
                print(f"✅ 成功获取到【{trade_date}】的行情数据，共 {len(df)} 只股票")
                return df, trade_date
        except Exception as e:
            print(f"❌ 尝试获取 {trade_date} 数据失败：{e}")
        
        # 往前推一天
        today -= timedelta(days=1)
        trade_date = today.strftime("%Y%m%d")
    
    print("❌ 连续5天都未获取到行情数据，请检查Tushare Token和账号状态")
    return None, None

def calculate_kdj(ts_code, days=30):
    """计算单只股票的KDJ值"""
    try:
        # 获取最近30天的日线数据
        df = ts.pro_bar(ts_code=ts_code, adj="qfq", limit=days)
        if df is None or len(df) < 20:
            return None, None
        
        # 倒序，从旧到新
        df = df.iloc[::-1].reset_index(drop=True)
        
        # 计算RSV
        low_min = df["low"].rolling(9).min()
        high_max = df["high"].rolling(9).max()
        df["rsv"] = (df["close"] - low_min) / (high_max - low_min) * 100
        
        # 计算K、D
        df["K"] = df["rsv"].ewm(span=3, adjust=False).mean()
        df["D"] = df["K"].ewm(span=3, adjust=False).mean()
        
        # 取最新值
        k = round(df["K"].iloc[-1], 2)
        d = round(df["D"].iloc[-1], 2)
        return k, d
    except:
        return None, None

# ========== 主程序 ==========
if __name__ == "__main__":
    # 1. 获取行情数据
    stock_df, latest_date = get_latest_trade_data()
    if stock_df is None:
        exit(1)
    
    # 2. 第一步筛选：换手率 > 5%
    print("🔍 第一步筛选：换手率 > 5% 的股票")
    high_turnover = stock_df[stock_df["turnover_rate"] > 5].copy()
    print(f"换手率>5%的股票：{len(high_turnover)} 只")

    # 3. 第二步筛选：KDJ(K、D均 < 50)
    print("🔍 第二步筛选：KDJ < 50 的股票")
    result = []
    for idx, row in high_turnover.iterrows():
        k, d = calculate_kdj(row["ts_code"])
        if k is not None and d is not None and k < 50 and d < 50:
            result.append({
                "股票代码": row["symbol"],
                "股票名称": row["name"],
                "换手率": round(row["turnover_rate"], 2),
                "K值": k,
                "D值": d
            })
    
    # 4. 输出结果
    if result:
        print(f"✅ 共筛选出 {len(result)} 只符合条件的股票")
        result_df = pd.DataFrame(result)
        print(result_df)
        
        # 保存结果文件
        result_df.to_csv("今日选股结果.csv", index=False, encoding="utf-8-sig")
        print("✅ 结果已保存为：今日选股结果.csv")
    else:
        print("ℹ️ 今日没有同时满足「换手率>5%」和「KDJ<50」的股票")
