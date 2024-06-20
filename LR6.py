import pandas as pd
import ta
from binance import Client
from dataclasses import dataclass
from typing import List


@dataclass
class Signal:
    time: pd.Timestamp
    asset: str
    quantity: float
    side: str
    entry: float
    take_profit: float
    stop_loss: float
    result: float
    closed_by: str


def create_signals(k_lines: pd.DataFrame) -> List[Signal]:
    signals = []
    for i in range(len(k_lines)):
        current_price = k_lines.iloc[i]['close']
        signal = None

        if k_lines.iloc[i]['cci'] < -100 and k_lines.iloc[i]['adx'] > 25:
            signal = 'sell'
        elif k_lines.iloc[i]['cci'] > 100 and k_lines.iloc[i]['adx'] > 25:
            signal = 'buy'
        
        if signal:
            if signal == "buy":
                stop_loss_price = round((1 - 0.01) * current_price, 1)
                take_profit_price = round((1 + 0.015) * current_price, 1)
            else:
                stop_loss_price = round((1 + 0.01) * current_price, 1)
                take_profit_price = round((1 - 0.015) * current_price, 1)

            signals.append(Signal(
                time=k_lines.iloc[i]['time'],
                asset='BTCUSDT',
                quantity=100,
                side=signal,
                entry=current_price,
                take_profit=take_profit_price,
                stop_loss=stop_loss_price,
                result=None,
                closed_by=None
            ))
    return signals


def perform_backtesting(k_lines: pd.DataFrame) -> List[Signal]:
    signals = create_signals(k_lines)
    results = []

    for signal in signals:
        start_index = k_lines[k_lines['time'] == signal.time].index[0]
        data_slice = k_lines.iloc[start_index:]

        for candle_id in range(len(data_slice)):
            current_candle = data_slice.iloc[candle_id]

            if (signal.side == "sell" and current_candle["low"] <= signal.take_profit) or (
                    signal.side == "buy" and current_candle["high"] >= signal.take_profit):
                signal.result = signal.take_profit - signal.entry if signal.side == 'buy' else (
                        signal.entry - signal.take_profit)
            elif (signal.side == "sell" and current_candle["high"] >= signal.stop_loss) or (
                    signal.side == "buy" and current_candle["low"] <= signal.stop_loss):
                signal.result = signal.stop_loss - signal.entry if signal.side == 'buy' else (
                        signal.entry - signal.stop_loss)

            if signal.result is not None:
                signal.closed_by = "TP" if signal.result > 0 else "SL"
                results.append(signal)
                break

    return results


def calculate_pnl(trade_list: List[Signal]) -> float:
    total_pnl = sum(trade.result for trade in trade_list)
    return total_pnl


def profit_factor(trade_list: List[Signal]) -> float:
    total_loss = sum(trade.result for trade in trade_list if trade.result < 0)
    total_profit = sum(trade.result for trade in trade_list if trade.result > 0)
    return total_profit / abs(total_loss) if total_loss != 0 else float('inf')


def calculate_statistics(trade_list: List[Signal]):
    print(f"Total PnL: {calculate_pnl(trade_list):.2f}")
    print(f"Profit Factor: {profit_factor(trade_list):.2f}")



client = Client()
k_lines = client.get_historical_klines(
    symbol="BTCUSDT",
    interval=Client.KLINE_INTERVAL_1MINUTE,
    start_str="1 week ago UTC",
    end_str="now UTC"
)


k_lines = pd.DataFrame(k_lines, columns=[
    'time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
    'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
    'taker_buy_quote_asset_volume', 'ignore'
])
k_lines['time'] = pd.to_datetime(k_lines['time'], unit='ms')
k_lines[['close', 'high', 'low', 'open']] = k_lines[['close', 'high', 'low', 'open']].astype(float)


k_lines['adx'] = ta.trend.ADXIndicator(k_lines['high'], k_lines['low'], k_lines['close']).adx()
k_lines['cci'] = ta.trend.CCIIndicator(k_lines['high'], k_lines['low'], k_lines['close']).cci()

# Perform backtesting
results = perform_backtesting(k_lines)

# Print results
for result in results:
    print(f"Time: {result.time}, Asset: {result.asset}, Quantity: {result.quantity}, Side: {result.side}, "
          f"Entry: {result.entry}, Take Profit: {result.take_profit}, Stop Loss: {result.stop_loss}, "
          f"Result: {result.result}, Closed_by: {result.closed_by}")

calculate_statistics(results)
