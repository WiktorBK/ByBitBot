from ta.trend import EMAIndicator, PSARIndicator, macd_diff


class Analyzer:

    def macd_signal(self, df, prev=False):

         # Add macd difference to dataframe
        macd = df.add_column("MACD Relation", macd_diff(df['Close']))
        x = 1 if prev else 0

         # Check different MACD conditions
        if macd[-1-x] > 0 and macd[-2-x] <= 0 or macd[-2-x] > 0 and macd[-3-x] <= 0 or macd[-3-x] > 0 and macd[-4-x] <= 0:
            if macd[-1-x] < 5 and macd[-1-x] > 0:
                return "BUY"
            
        elif macd[-1-x] < 0 and macd[-2-x] >= 0 or macd[-2-x] < 0 and macd[-3-x] >= 0 or macd[-3-x] < 0 and macd[-4-x] >= 0:
            if macd[-1-x] > -5 and macd[-1-x] < 0:
                return "SELL"
        else:
            return "NO SIGNAL"
        

    def psar_signal(self, df, prev=False):

         # Add PSAR prices to dataframe
        psar_down = df.add_column("pSAR_down", PSARIndicator(df['High'], df['Low'], df['Close']).psar_down())
        psar_up = df.add_column("pSAR_up", PSARIndicator(df['High'], df['Low'], df['Close']).psar_up())
        x = 1 if prev else 0

         # Check different PSAR conditions
        if df.isnull(psar_down[-2-x]) == False and df.isnull(psar_down[-1-x]) or df.isnull(psar_down[-3-x]) == False and df.isnull(psar_down[-2-x]) \
                or df.isnull(psar_down[-4-x]) == False and df.isnull(psar_down[-3-x]):
            return "BUY"
        elif df.isnull(psar_down[-2-x]) and df.isnull(psar_down[-1-x]) == False or df.isnull(psar_down[-3-x]) and df.isnull(psar_down[-2-x]) == False \
                or df.isnull(psar_down[-4-x]) and df.isnull(psar_down[-3-x]) == False:
            return "SELL"
        else:
            return "NO SIGNAL"
        
    
    def ema_signal(self, df, prev=False):

        ema100 = df.add_column("Ema100", EMAIndicator(df['Close'], 100).ema_indicator())
        x = 1 if prev else 0

        # Check EMA conditions
        if ema100[-1-x] <= ema100[-1-x]: return "Sell"

        elif df['Close'][-1-x] >= ema100[-1-x]: return "Buy"