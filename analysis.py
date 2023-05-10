from ta.trend import EMAIndicator, PSARIndicator, macd_diff
import pandas as pd


class Analyser:

    def macd_signal(df, prev=False):

         # Add macd difference to dataframe
        df["MACD Relation"] = macd_diff(df['Close'])
        macd = df["MACD Relation"]
        x = 1 if prev else 0

        '''
          Check different MACD conditions
         
            make sure that the difference isn't to high already

            signal will be 'buy' or 'sell' for 3 candles since appearing.
            eg: on timeframe: 3min -> signal opportunity for 9 minutes (3*3).

            if prev == True signals will be checked for previous candle
        '''
        if macd[-1-x] > 0 and macd[-2-x] <= 0 or macd[-2-x] > 0 and macd[-3-x] <= 0 or macd[-3-x] > 0 and macd[-4-x] <= 0:
            if macd[-1-x] < 5 and macd[-1-x] > 0:
                return "Buy"
            
        elif macd[-1-x] < 0 and macd[-2-x] >= 0 or macd[-2-x] < 0 and macd[-3-x] >= 0 or macd[-3-x] < 0 and macd[-4-x] >= 0:
            if macd[-1-x] > -5 and macd[-1-x] < 0:
                return "Sell"
        else:
            return "NO SIGNAL"

    def psar_signal(df, prev=False):



         # Add PSAR prices to dataframe
        df["pSAR_down"] = PSARIndicator(df['High'], df['Low'], df['Close']).psar_down()
        df["pSAR_up"] =  PSARIndicator(df['High'], df['Low'], df['Close']).psar_up()
        psar_down = df["pSAR_down"]
        x = 1 if prev else 0

        '''
          Check different PSAR conditions

            signal will be 'buy' or 'sell' for 3 candles since appearing.
            eg: on timeframe: 3min -> signal opportunity for 9 minutes (3*3).

            if prev == True signals will be checked for previous candle
        '''
        if pd.isna(psar_down[-2-x]) == False and pd.isna(psar_down[-1-x]) or pd.isna(psar_down[-3-x]) == False and pd.isna(psar_down[-2-x]) \
                or pd.isna(psar_down[-4-x]) == False and pd.isna(psar_down[-3-x]):
            return "Buy"
        elif pd.isna(psar_down[-2-x]) and pd.isna(psar_down[-1-x]) == False or pd.isna(psar_down[-3-x]) and pd.isna(psar_down[-2-x]) == False \
                or pd.isna(psar_down[-4-x]) and pd.isna(psar_down[-3-x]) == False:
            return "Sell"
        
    
    def ema_signal(self, df, prev=False):

        ema100 = df.add_column("Ema100", EMAIndicator(df['Close'], 100).ema_indicator())
        x = 1 if prev else 0

        # Check EMA conditions
        if ema100[-1-x] <= ema100[-1-x]: return "Sell"

        elif df['Close'][-1-x] >= ema100[-1-x]: return "Buy"