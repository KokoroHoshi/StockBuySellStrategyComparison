import pandas as pd

def DollarCostAveraging(data: pd.DataFrame, pickup_date: str ="first", skip_non_trade_day: bool = True) -> pd.Series:
    # skip_non_trade_day=False時標註的日期與實際交易日有差異
    if pickup_date == "first":
        buy_dates_df = data.resample('MS').first()
    elif pickup_date == "last":
        buy_dates_df = data.resample('ME').last()

    if skip_non_trade_day:
        buy_dates = buy_dates_df[buy_dates_df.index.isin(data.index)].index

    return buy_dates

def MovingAverageCrossover(data: pd.DataFrame, short_ma_period: int, long_ma_period: int) -> dict:
    short_ma = data['Close(NTD)'].rolling(window=short_ma_period).mean()
    long_ma = data['Close(NTD)'].rolling(window=long_ma_period).mean()

    buy_signals = (short_ma.shift(1) <= long_ma.shift(1)) & (short_ma > long_ma)
    sell_signals = (short_ma.shift(1) >= long_ma.shift(1)) & (short_ma < long_ma)

    buy_dates = buy_signals[buy_signals].index
    sell_dates = sell_signals[sell_signals].index

    ma_info = {
        'short_ma_name':f'MA_{short_ma_period}',
        'short_ma':short_ma,
        'long_ma_name':f'MA_{long_ma_period}',
        'long_ma':long_ma, 'buy_dates':buy_dates,
        'sell_dates':sell_dates
    }

    return ma_info

