
import time
import calendar
from datetime import datetime

import pandas as pd

from bybit import Bybit
from config import *
from analysis import Analyser

class Bot: 

    def __init__(self):
        self.bybit = Bybit(AKEY, ASECRET)
        

    def get_index(self, trades):

        #handle api behaviour
        for i in range(len(trades)):
            ep = trades[i]['entry_price']
            if ep != 0: return i
    
    def calculate_takeprofit(entry_price, sl, side):

        # Calculate takeprofit based on open price, stoploss price and side
        sl_percent = abs((1 - sl/entry_price))
        tp_percent = sl_percent * 1.25
        if side == "Buy": take_profit = entry_price + entry_price * tp_percent
        elif side == "Sell": take_profit = entry_price - entry_price * tp_percent
        return round(take_profit, 2)

    def in_trade(self):

        x = self.get_index(self.bybit.session.my_position(symbol=SYMBOL)['result'])

        # set the entry price
        ep = 0 if x == None else self.bybit.get_entry_price(x)

        return True if ep != 0 else False
    
    def print_info(self, data):
        macd=Analyser.macd_signal(data)
        psar=Analyser.psar_signal(data)
        ema=Analyser.ema_signal(data)
        lp = self.bybit.get_last_price()
        print(f"Current signals:\nMACD: {macd}; PSAR: {psar}; EMA: {ema}\nLast price of {SYMBOL}: {lp}\n")



            

    







