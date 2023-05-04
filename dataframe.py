import pandas as pd

import traceback


class CandleData:

    def __init__(self, data):
        self.data = data
        self.format_data = self.format_df()

    def format_df(self):
        df = pd.DataFrame(self.data[:-1]) # cut last data candle
        df = df.iloc[:, 5:11] # reduce column amount
        df.columns = ['Time', 'Volume', 'Open', 'High', 'Low', 'Close']  # specify columns
        df = df.set_index('Time') 
        df.index = pd.to_datetime(df.index, unit='s')
        df = df.astype(float)
        return df
    
    def add_column(self, col_name, value):
        try:
            self.format_data[col_name] = value
        except:
            return f"Failed to create new column:\n {traceback.format_exc()}"

    def isnull(self, value):
        try:
            return pd.isna(value)
        except: 
            return f"Failed to check if the value is null:\n {traceback.format_exc()}"