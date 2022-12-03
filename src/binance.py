"""
File with Binance trading interface
"""
import requests


class BinanceTradingInterface:
    """ All trading features for Binance """

    @staticmethod
    def get_pair_price(pair: str) -> (float, None):
        """ Returns last price of the given pair """

        try:
            response = requests.get('https://api.binance.com/api/v3/ticker/price',
                                    params={'symbol': pair})
            data = response.json()
            return float(data['price'])
        except:
            return None

    @staticmethod
    def get_historic_data(pair: str, timeframe: str = '15m', candles_number: int = 500) -> (list, None):
        """ Returns historic candlestick data """

        try:
            response = requests.get('https://api.binance.com/api/v3/klines',
                                    params={'symbol': pair,
                                            'interval': timeframe,
                                            'limit': candles_number})
            data = response.json()

            # Reformatting data, extracting only date + OHLC
            result = [[float(_) for _ in i[:5]] for i in data]
            return result
        except:
            return None
