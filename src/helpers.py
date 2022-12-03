"""
File with all the calculations functions
"""
import os
import time
import random
import secrets
import pandas as pd
import mplfinance as mpf

from src import binance


class TradingStrategyOne:
    """ All functions related to trading strategy #1

    We are making a buy every time price touches the given SMA from the support side and then either taking profit or
    loss regarding the given parameters.
    If price is below the SMA, the purchase happens on the close of the candle that breaks the SMA.
    """

    def __init__(self, pair: str, timeframe: str, candles_number: int, sma_diapason: int, tp_percent: int,
                 sl_percent: int):
        self.pair = pair
        self.timeframe = timeframe
        self.candles_number = candles_number
        self.sma_diapason = sma_diapason

        self.tp_percent = tp_percent
        self.sl_percent = sl_percent

        self.prices_data = binance.BinanceTradingInterface.get_historic_data(
            pair=pair,
            timeframe=timeframe,
            candles_number=candles_number
        )

        # Bringing timestamps from ms to s
        for element in self.prices_data:
            element[0] = int(element[0] / 100000)

        # Loading data to pandas
        self.data_frame = pd.DataFrame(self.prices_data, columns=['date', 'open', 'high', 'low', 'close'])

    def get_trades(self) -> dict:
        """ Calculates all the trades """

        # Adding SMA data column to our data frame
        self._add_sma()

        _csv_data = self.data_frame.to_csv()
        _reformatted_list = _csv_data.split('\n')[1:-1]
        _reformatted_data = [i.split(',') for i in _reformatted_list]

        # List of trades that are made
        trades = []

        for candle in _reformatted_data:

            # Current candle data
            _sma = float(candle[-1]) if candle[-1] != '' else None
            _open = float(candle[2])
            _close = float(candle[5])
            _high = float(candle[3])
            _low = float(candle[4])
            _candle_number = int(candle[0])

            # Previous candle data
            previous_candle = None
            _prev_sma = None
            _prev_open = None
            _prev_close = None
            _prev_high = None
            _prev_low = None

            if _reformatted_data.index(candle) != 0:
                previous_candle = _reformatted_data[_reformatted_data.index(candle) - 1]

                _prev_sma = float(previous_candle[-1]) if previous_candle[-1] != '' else None
                _prev_open = float(previous_candle[2])
                _prev_close = float(previous_candle[5])
                _prev_high = float(previous_candle[3])
                _prev_low = float(previous_candle[4])

            # If SMA is present on the given candle
            if _sma is not None:

                # We have no orders to close -> we can only open
                if all([len(trades) > 0 and trades[-1]['position_action'] == 'close']) or len(trades) == 0:

                    # Price breaks SMA
                    # ::: if previous candle's high was was under the SMA
                    # ::: the entry point is on candle close
                    if (_low <= _sma < _high) and all([previous_candle and _prev_sma and _prev_high < _prev_sma]):
                        trades.append(
                            {'position_action': 'open',
                             'entry_price': round(_close, 2),
                             'candle_number': _candle_number}
                        )

                    # Price touches SMA
                    # ::: the entry point is on candle touching SMA
                    elif _low <= _sma < _high:
                        trades.append(
                            {'position_action': 'open',
                             'entry_price': round(_sma, 2),
                             'candle_number': _candle_number}
                        )

                # We can close the order if it has reached SL or TP
                else:
                    open_trade = trades[-1]
                    min_price_change = _low - open_trade['entry_price']
                    max_price_change = _high - open_trade['entry_price']

                    # First checking for SL; going in direction Open -> Low -> High -> Close
                    if min_price_change < 0 and abs(
                            min_price_change / open_trade['entry_price']) * 100 >= self.sl_percent:
                        trades.append(
                            {'position_action': 'close',
                             'close_price': open_trade['entry_price'] - round(
                                 (open_trade['entry_price'] / 100) * self.sl_percent, 2),
                             'result': 'loss',
                             'candle_number': _candle_number}
                        )

                    # Checking TP
                    elif max_price_change > 0 and abs(
                            max_price_change / open_trade['entry_price']) * 100 >= self.tp_percent:
                        trades.append(
                            {'position_action': 'close',
                             'close_price': open_trade['entry_price'] + round(
                                 (open_trade['entry_price'] / 100) * self.tp_percent, 2),
                             'result': 'profit',
                             'candle_number': _candle_number}
                        )

        chart_image_path = self.render_chart()
        return {'trades': trades,
                'chart_image_path': chart_image_path,
                'result_text': self._get_trades_results(trades),
                'trades_number': len(trades)}

    def render_chart(self):
        """ Rendering chart as picture and returning path to it """

        self.data_frame['date'] = pd.to_datetime(self.data_frame['date'], unit='s')
        self.data_frame = self.data_frame.set_index('date')

        path = f'./images/render-{secrets.token_urlsafe(10)}.png'
        mpf.plot(self.data_frame, type='candle', mav=(2, self.sma_diapason), savefig=path)
        return path

    def _get_trades_results(self, trades: list):
        """ Calculates overall result. Returns as string lost/earned XX% """

        result = 0
        for trade in trades:
            if trade['position_action'] == 'close':
                result += self.tp_percent if trade['result'] == 'profit' else -self.sl_percent

        if result >= 0:
            return f'earned {result}% 🤩'
        else:
            return f'lost {result}% 🥲'

    def _add_sma(self):
        """ Adding SMA to the dataset """
        self.data_frame[f'SMA({self.sma_diapason})'] = self.data_frame['close'].rolling(self.sma_diapason).mean()


def get_random_calculations():
    """ Returning calculations with precoded data """

    data = {'pair': random.choice(['BTCUSDT', 'ETHUSDT', 'BNBUSDT']),
            'timeframe': random.choice(['5m', '15m', '1h', '4h']),
            'candles': random.choice([250, 300, 350, 400, 500, 1000]),
            'ma': random.choice([10, 35, 50, 99]),
            'sl': random.randint(2, 5),
            'tp': random.randint(2, 10)}

    result = TradingStrategyOne(
        pair=data['pair'],
        timeframe=data['timeframe'],
        candles_number=data['candles'],
        sma_diapason=data['ma'],
        sl_percent=data['sl'],
        tp_percent=data['tp']
    ).get_trades()
    result['calculations_data'] = data
    return result


def get_example_calculations():
    """ Returning calculations with precoded data """

    data = {'pair': 'YFIUSDT',
            'timeframe': '1d',
            'candles': 1000,
            'ma': 50,
            'sl': 3,
            'tp': 15}

    result = TradingStrategyOne(
        pair=data['pair'],
        timeframe=data['timeframe'],
        candles_number=data['candles'],
        sma_diapason=data['ma'],
        sl_percent=data['sl'],
        tp_percent=data['tp']
    ).get_trades()
    result['calculations_data'] = data
    return result


def delete_render_image(path: str):
    """ Deleting render image after it's been displayed (call in thread) """
    time.sleep(10)
    os.remove(path)
