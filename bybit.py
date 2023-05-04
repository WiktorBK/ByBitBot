from pybit.usdt_perpetual import HTTP
import traceback
import calendar
import datetime

from config import *
from dataframe import CandleData




class Bybit:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = self.open_session()


    def open_session(self):
        session = HTTP( "https://api.bybit.com", api_key=self.api_key, api_secret=self.api_secret, request_timeout=60)
        return session
    
    def get_data(self, since):

        try:
            data = self.session.query_kline(
            symbol=SYMBOL, interval=INTERVAL,
            **{'from': since} 
            )['result']

            return CandleData.format_df(data)

        except Exception: 
            print(f"couldn't import data:\n {traceback.format_exc()}")


bybit = Bybit(AKEY, ASECRET)


print(bybit.get_data(calendar.timegm(datetime.datetime.utcnow().utctimetuple()) - 3600))




