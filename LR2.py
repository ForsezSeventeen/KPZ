import pandas as pd
from binance import Client
from time import time, ctime

def calculate_rsi(prices, period):
    price_diff = prices.diff()
    gains = price_diff.clip(lower=0)
    losses = -price_diff.clip(upper=0)
    avg_gain = gains.ewm(span=period, adjust=False).mean()
    avg_loss = losses.ewm(span=period, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_rsi_data(asset, periods):
    client = Client()
    end_time = int(time() * 1000)
    start_time = end_time - 24 * 60 * 60 * 1000
    k_lines = client.get_historical_klines(
        symbol=asset,
        interval=Client.KLINE_INTERVAL_1MINUTE,
        start_str=ctime(start_time / 1000),
        end_str=ctime(end_time / 1000)
    )
    df = pd.DataFrame(k_lines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df['close'] = df['close'].astype(float)
    result = pd.DataFrame({'time': df['time']})
    for period in periods:
        rsi_values = calculate_rsi(df['close'], period)
        result[f'RSI_{period}'] = rsi_values
    return result

asset = "BTCUSDT"
periods = [14, 27, 100]
rsi_data = get_rsi_data(asset, periods)
print(rsi_data)
