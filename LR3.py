import pandas as pd
import ta
from matplotlib import pyplot as plt
from binance.client import Client
from datetime import datetime, timedelta

def fetch_data(asset, interval, days):
    client = Client()
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    k_lines = client.get_historical_klines(
        symbol=asset,
        interval=interval,
        start_str=start_time.strftime("%Y-%m-%d %H:%M:%S"),
        end_str=end_time.strftime("%Y-%m-%d %H:%M:%S")
    )
    return k_lines

def process_data(k_lines):
    k_lines_df = pd.DataFrame(k_lines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    k_lines_df['time'] = pd.to_datetime(k_lines_df['time'], unit='ms')
    k_lines_df[['open', 'high', 'low', 'close']] = k_lines_df[['open', 'high', 'low', 'close']].astype(float)
    
    # Расчет индикаторов
    k_lines_df['RSI'] = ta.momentum.RSIIndicator(k_lines_df['close']).rsi()
    k_lines_df['CCI'] = ta.trend.CCIIndicator(k_lines_df['high'], k_lines_df['low'], k_lines_df['close']).cci()
    k_lines_df['MACD'] = ta.trend.MACD(k_lines_df['close']).macd()
    k_lines_df['ATR'] = ta.volatility.AverageTrueRange(k_lines_df['high'], k_lines_df['low'], k_lines_df['close']).average_true_range()
    k_lines_df['ADX'] = ta.trend.ADXIndicator(k_lines_df['high'], k_lines_df['low'], k_lines_df['close']).adx()
    
    # Сигналы
    k_lines_df['RSI_buy'] = (k_lines_df['RSI'] < 30) & (k_lines_df['RSI'].shift() >= 30)
    k_lines_df['RSI_sell'] = (k_lines_df['RSI'] > 70) & (k_lines_df['RSI'].shift() <= 70)
    k_lines_df['CCI_buy'] = (k_lines_df['CCI'] < -100) & (k_lines_df['CCI'].shift() >= -100)
    k_lines_df['CCI_sell'] = (k_lines_df['CCI'] > 100) & (k_lines_df['CCI'].shift() <= 100)
    k_lines_df['MACD_buy'] = (k_lines_df['MACD'].shift() < 0) & (k_lines_df['MACD'] > 0)
    k_lines_df['MACD_sell'] = (k_lines_df['MACD'].shift() > 0) & (k_lines_df['MACD'] < 0)
    k_lines_df['ATR_buy'] = k_lines_df['ATR'] > k_lines_df['ATR'].shift()
    k_lines_df['ATR_sell'] = k_lines_df['ATR'] < k_lines_df['ATR'].shift()
    k_lines_df['ADX_buy'] = (k_lines_df['ADX'] > 25) & (k_lines_df['ADX'].shift() <= 25)
    k_lines_df['ADX_sell'] = (k_lines_df['ADX'] < 25) & (k_lines_df['ADX'].shift() >= 25)
    
    return k_lines_df

def plot_data(k_lines_df):
    plt.figure(figsize=(14, 10))
    
    # Закрытие
    plt.subplot(6, 1, 1)
    plt.plot(k_lines_df['time'], k_lines_df['close'], label='Close Price')
    plt.title('Close Price')
    
    # RSI
    plt.subplot(6, 1, 2)
    plt.plot(k_lines_df['time'], k_lines_df['RSI'], label='RSI', color='purple')
    plt.scatter(k_lines_df.loc[k_lines_df['RSI_buy'], 'time'], k_lines_df.loc[k_lines_df['RSI_buy'], 'RSI'], marker='^', color='green', label='Buy Signal')
    plt.scatter(k_lines_df.loc[k_lines_df['RSI_sell'], 'time'], k_lines_df.loc[k_lines_df['RSI_sell'], 'RSI'], marker='v', color='red', label='Sell Signal')
    plt.title('RSI')
    plt.legend()
    
    # MACD
    plt.subplot(6, 1, 3)
    plt.plot(k_lines_df['time'], k_lines_df['MACD'], label='MACD', color='green')
    plt.scatter(k_lines_df.loc[k_lines_df['MACD_buy'], 'time'], k_lines_df.loc[k_lines_df['MACD_buy'], 'MACD'], marker='^', color='green', label='Buy Signal')
    plt.scatter(k_lines_df.loc[k_lines_df['MACD_sell'], 'time'], k_lines_df.loc[k_lines_df['MACD_sell'], 'MACD'], marker='v', color='red', label='Sell Signal')
    plt.title('MACD')
    plt.legend()
    
    # ATR
    plt.subplot(6, 1, 4)
    plt.plot(k_lines_df['time'], k_lines_df['ATR'], label='ATR', color='black')
    plt.scatter(k_lines_df.loc[k_lines_df['ATR_buy'], 'time'], k_lines_df.loc[k_lines_df['ATR_buy'], 'ATR'], marker='^', color='green', label='Buy Signal')
    plt.scatter(k_lines_df.loc[k_lines_df['ATR_sell'], 'time'], k_lines_df.loc[k_lines_df['ATR_sell'], 'ATR'], marker='v', color='red', label='Sell Signal')
    plt.title('ATR')
    plt.legend()
    
    # ADX
    plt.subplot(6, 1, 5)
    plt.plot(k_lines_df['time'], k_lines_df['ADX'], label='ADX', color='black')
    plt.scatter(k_lines_df.loc[k_lines_df['ADX_buy'], 'time'], k_lines_df.loc[k_lines_df['ADX_buy'], 'ADX'], marker='^', color='green', label='Buy Signal')
    plt.scatter(k_lines_df.loc[k_lines_df['ADX_sell'], 'time'], k_lines_df.loc[k_lines_df['ADX_sell'], 'ADX'], marker='v', color='red', label='Sell Signal')
    plt.title('ADX')
    plt.legend()
    
    # CCI
    plt.subplot(6, 1, 6)
    plt.plot(k_lines_df['time'], k_lines_df['CCI'], label='CCI', color='black')
    plt.scatter(k_lines_df.loc[k_lines_df['CCI_buy'], 'time'], k_lines_df.loc[k_lines_df['CCI_buy'], 'CCI'], marker='^', color='green', label='Buy Signal')
    plt.scatter(k_lines_df.loc[k_lines_df['CCI_sell'], 'time'], k_lines_df.loc[k_lines_df['CCI_sell'], 'CCI'], marker='v', color='red', label='Sell Signal')
    plt.title('CCI')
    plt.legend()
    
    plt.tight_layout()
    plt.show()

# Загрузка данных
asset = "BTCUSDT"
interval = Client.KLINE_INTERVAL_1MINUTE
days = 1
k_lines = fetch_data(asset, interval, days)

# Обработка данных
k_lines_df = process_data(k_lines)

# Визуализация данных
plot_data(k_lines_df)
