from pybit.usdt_perpetual import HTTP
import pandas as pd

import traceback
import calendar
from datetime import datetime

from config import *



class Bybit():
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = self.open_session()

    def calculate_since(self):
        now = datetime.utcnow()
        unixtime = calendar.timegm(now.utctimetuple())
        return unixtime - 21600

    def open_session(self):
        try:
            session = HTTP( "https://api.bybit.com", api_key=self.api_key, api_secret=self.api_secret, request_timeout=60)
            return session
        except: print(f"Session could not be opened: {traceback.format_exc()}")
    
    def get_data(self):
        try:
            data = self.session.query_kline(symbol=SYMBOL, interval=INTERVAL,**{'from': self.calculate_since()} )['result']
            return data  
        except Exception: 
            print(f"couldn't import data:\n {traceback.format_exc()}")

    def get_format_data(self):

        data = self.get_data()

        try: 
            data = pd.DataFrame(data[:-1]) # cut last data candle
            data = data.iloc[:, 5:11] # reduce column amount
            data.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']  # specify columns
            data = data.set_index('Time') 
            data.index = pd.to_datetime(data.index, unit='s')
            data = data.astype(float)
        except:
            print(f"An error occured while formatting data: {traceback.format_exc()}")
        return data

    def place_order(self, side):
        try:
            self.session.place_active_order(
                symbol=SYMBOL, side=side, order_type="Market",qty=QTY,
                time_in_force="GoodTillCancel",reduce_only=False,close_on_trigger=False)
        except:
            print("couldn't place order:\n" + traceback.format_exc())
            
    def get_last_price(self):
        try: return  self.session.latest_information_for_symbol(symbol=SYMBOL)['result'][0]['index_price']
        except: print("couldn't get last price:\n" + traceback.format_exc())
            
    def get_entry_price(self, idx):
        try: return self.session.my_position(symbol=SYMBOL)['result'][idx]['entry_price']
        except: print("couldn't get entry price:\n" + traceback.format_exc())

    def set_stops(self, sl, tp, side):
        try: self.session.set_trading_stop(symbol=SYMBOL, side=side, stop_loss=sl, take_profit=tp)
        except: print("couldn't set stoploss and takeprofit:\n" + traceback.format_exc())





