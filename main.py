import pandas as pd
import time
import calendar
from pybit import HTTP
from datetime import datetime
from ta.trend import EMAIndicator, PSARIndicator, macd_diff
from datetime import datetime
from notifications import ns, nto, ntc, nupd, ncon, nlc, nrc, nres
import secrets


symbol = 'ETHUSDT'
tick_interval = '3'
qty = 0.01

now = datetime.utcnow()
unixtime = calendar.timegm(now.utctimetuple())
since = unixtime - 60 * 60 * 3*2

# Opening bybit session
session = HTTP(
    "https://api.bybit.com",
    api_key=secrets.apikey,
    api_secret=secrets.apisecret,
    request_timeout=60)

def get3minutedata(symbol):
    # Get Data
    try:
        data = session.query_kline(
            symbol=symbol,
            interval='3',
            **{'from': since}
        )['result']
    except:
        print("Lost Connection")
        print("Reconnecting...")
        time.sleep(60)
        data = session.query_kline(
            symbol=symbol,
            interval='3',
            **{'from': since}
        )['result']
        nrc(datetime.now().strftime("%H:%M:%S"))
        
    # Format Data
    df = pd.DataFrame(data[:-1])
    df = df.iloc[:, 5:11]
    df.columns = ['Time', 'Volume', 'Open', 'High', 'Low', 'Close']
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index, unit='ms')
    df = df.astype(float)
    return df

def check_for_macd_signal(dataframe):
    df = dataframe
    # Adding MACD difference to dataframe
    df['MACD relation'] = macd_diff(df['Close'])
    # Checking different MACD conditions
    if df['MACD relation'][-1] > 0 \
            and df['MACD relation'][-2] <= 0 or df['MACD relation'][-2] > 0 \
            and df['MACD relation'][-3] <= 0 or df['MACD relation'][-3] > 0 \
            and df['MACD relation'][-4] <= 0:
        if df['MACD relation'][-1] < 5 and df['MACD relation'][-1] > 0:
            return "Buy"
    elif df['MACD relation'][-1] < 0 \
            and df['MACD relation'][-2] >= 0 or df['MACD relation'][-2] < 0 \
            and df['MACD relation'][-3] >= 0 or df['MACD relation'][-3] < 0 \
            and df['MACD relation'][-4] >= 0:
        if df['MACD relation'][-1] > -5 and df['MACD relation'][-1] < 0:
            return "Sell"
    else:
        return "NO SIGNAL"
    
def check_for_psar_signal(dataframe):
    df = dataframe
    # Adding PSAR prices to dataframe
    df['pSAR_down'] = PSARIndicator(
        df['High'], df['Low'], df['Close']).psar_down()
    df['pSAR_up'] = PSARIndicator(df['High'], df['Low'], df['Close']).psar_up()
    # Checking different PSAR conditions
    if pd.isna(df['pSAR_down'][-2]) == False and pd.isna(df['pSAR_down'][-1]) == True or pd.isna(df['pSAR_down'][-3]) == False and pd.isna(df['pSAR_down'][-2]) == True \
            or pd.isna(df['pSAR_down'][-4]) == False and pd.isna(df['pSAR_down'][-3]) == True:
        return "Buy"
    elif pd.isna(df['pSAR_down'][-2]) == True and pd.isna(df['pSAR_down'][-1]) == False or pd.isna(df['pSAR_down'][-3]) == True and pd.isna(df['pSAR_down'][-2]) == False \
            or pd.isna(df['pSAR_down'][-4]) == True and pd.isna(df['pSAR_down'][-3]) == False:
        return "Sell"
    else:
        return "NO SIGNAL"
    
def check_for_ema_signal(dataframe):
    df = dataframe
    # Adding 100 EMA price to dataframe
    df['Ema100'] = EMAIndicator(df['Close'], 100).ema_indicator()
    # Checking EMA conditions
    if df['Close'][-1] <= df['Ema100'][-1]:
        return "Sell"
    elif df['Close'][-1] >= df['Ema100'][-1]:
        return "Buy"
    
def psar_price(dataframe):
    # Returning PSAR price
    df = dataframe
    df['pSAR'] = PSARIndicator(df['High'], df['Low'], df['Close']).psar()
    return df['pSAR'][-1]

def calculate_takeprofit(open_price, stop_loss, side):
    # Calculating takeprofit based on open price, stoploss and side
    stop_loss_percentage = abs((1 - stop_loss/open_price))
    take_profit_percentage = stop_loss_percentage * 1.25
    if side == "Buy":
        take_profit = open_price + open_price * take_profit_percentage
    elif side == "Sell":
        take_profit = open_price - open_price * take_profit_percentage
    take_profit = round(take_profit, 2)
    return take_profit

def place_active_order(qty, side):
    session.place_active_order(
        symbol=symbol,
        side=side,
        order_type="Market",
        qty=qty,
        time_in_force="GoodTillCancel",
        reduce_only=False,
        close_on_trigger=False
    )
    
def calculate_pnl(qty, entry_price, exit_price, sl, tp):
    tp_distance = abs(float(tp) - float(exit_price))
    sl_distance = abs(float(sl) - float(exit_price))
    if tp_distance < sl_distance:
        hitby = "tp"
    elif sl_distance < tp_distance:
        hitby = "sl"
    else:
        return "Unable to calculate PNL"

    entry_size = qty * float(entry_price)
    if hitby == "tp": 
        close_size = qty * tp 
        profit = abs(close_size - entry_size)
    elif hitby == "sl": 
        close_size = qty * sl
        profit = abs(close_size - entry_size) * -1
    entry_fee = entry_size * 0.00075 
    close_fee = close_size * 0.00075
    pnl = round(profit - entry_fee - close_fee, 5)
    return pnl

def setnewstoploss(sl, entry_price, side):
    diff = abs(entry_price - sl)
    new_diff = diff/2
    if sl > entry_price:
        new_sl = entry_price + new_diff
    elif sl < entry_price:
        new_sl = entry_price - new_diff
    session.set_trading_stop(symbol=symbol, stop_loss=new_sl, side=side)
    
def get_correct_index(list):
    leng = len(list)
    for i in range(leng):
        ep = list[i]['entry_price']
        if ep != 0:
            return i
        
def is_at_best_price(price_now, open_price):
    if abs(float(open_price) - float(price_now)) <= 3:
        return True
    else:
        return False
    
def prev_signals_agreement(df):
    df['Ema100'] = EMAIndicator(df['Close'], 100).ema_indicator()
    # Checking EMA conditions
    if df['Close'][-2] <= df['Ema100'][-2]:
        ema_signal = "Sell"
    elif df['Close'][-2] >= df['Ema100'][-2]:
        ema_signal = "Buy"
    # Adding PSAR prices to dataframe
    df['pSAR_down'] = PSARIndicator(
        df['High'], df['Low'], df['Close']).psar_down()
    df['pSAR_up'] = PSARIndicator(df['High'], df['Low'], df['Close']).psar_up()
    # Checking different PSAR conditions
    if pd.isna(df['pSAR_down'][-3]) == False and pd.isna(df['pSAR_down'][-2]) == True or pd.isna(df['pSAR_down'][-4]) == False and pd.isna(df['pSAR_down'][-3]) == True \
            or pd.isna(df['pSAR_down'][-5]) == False and pd.isna(df['pSAR_down'][-4]) == True:
        psar_signal = "Buy"
    elif pd.isna(df['pSAR_down'][-3]) == True and pd.isna(df['pSAR_down'][-2]) == False or pd.isna(df['pSAR_down'][-4]) == True and pd.isna(df['pSAR_down'][-3]) == False \
            or pd.isna(df['pSAR_down'][-5]) == True and pd.isna(df['pSAR_down'][-4]) == False:
        psar_signal = "Sell"
    else:
        psar_signal = "NO SIGNAL"
    macd_signal = "NO SiGNAL"
       # Adding MACD difference to dataframe
    df['MACD relation'] = macd_diff(df['Close'])
    # Checking different MACD conditions
    if df['MACD relation'][-2] > 0 \
            and df['MACD relation'][-3] <= 0 or df['MACD relation'][-3] > 0 \
            and df['MACD relation'][-4] <= 0 or df['MACD relation'][-4] > 0 \
            and df['MACD relation'][-5] <= 0:
        if df['MACD relation'][-2] < 5 and df['MACD relation'][-2] > 0:
            macd_signal = "Buy"
    elif df['MACD relation'][-2] < 0 \
            and df['MACD relation'][-3] >= 0 or df['MACD relation'][-3] < 0 \
            and df['MACD relation'][-4] >= 0 or df['MACD relation'][-4] < 0 \
            and df['MACD relation'][-5] >= 0:
        if df['MACD relation'][-2] > -5 and df['MACD relation'][-2] < 0:
            macd_signal = "Sell"
    else:
        macd_signal = "NO SIGNAL"
    if macd_signal == psar_signal == ema_signal:
        return True
    else:
        return False
    
# Main Function
def run():
    # Starting main loop
    trade_id = 0
    check_no = 1

    while True:
        x = get_correct_index(session.my_position(symbol=symbol)['result'])
        if x == None:
            my_position_entry_price = 0
        else:
            my_position_entry_price = session.my_position(
                symbol=symbol)['result'][x]['entry_price']

        print("\n### Trading Bot is now checking for signals ###\n")


        while True:
            # When trade is already opened
            if my_position_entry_price != 0:
                print("\nTrade is already being executed")
                stoploss = session.my_position(symbol=symbol)[
                    'result'][x]['stop_loss']
                tp = session.my_position(symbol=symbol)[
                    'result'][x]['take_profit']
                side = session.my_position(symbol=symbol)['result'][x]['side']
                entry_hour = datetime.now().strftime("%H:%M:%S")
           
                # Printing some information
                print(f"open price: {my_position_entry_price}")
                print(f"stop loss: {stoploss}")
                print(f"side: {side}")
                print(f"take profit: {tp}")
                print(f"{entry_hour}")
                break
                
            # Checking data every 2 seconds
            df = get3minutedata(symbol)
            print(f"{symbol} {check_no}\nPrev Signals: {prev_signals_agreement(df)}\nPsar Signal: {check_for_psar_signal(df)}\nMacd Signal: {check_for_macd_signal(df)}\nEMA Signal: {check_for_ema_signal(df)}\n{datetime.now()}\n")
    
            
            open_price = df['Close'][-1]
            last_price = session.latest_information_for_symbol(symbol=symbol)['result'][0]['index_price']
            # Checking if the signals are the same
            if check_for_psar_signal(df) == check_for_ema_signal(df) == check_for_macd_signal(df) and my_position_entry_price == 0 and is_at_best_price(last_price, open_price) and prev_signals_agreement(df) == False:

                # If signals are correct postion opens and then we break out of the loop
                side = check_for_ema_signal(df)
                stoploss = float(psar_price(df))
                stoploss = round(stoploss, 2)
                now = datetime.now()
                entry_hour = now.strftime("%H:%M:%S")

                place_active_order(qty, side)
                x = get_correct_index(session.my_position(symbol=symbol)['result'])
                my_position_entry_price = session.my_position(symbol=symbol)['result'][x]['entry_price']
                tp = calculate_takeprofit(my_position_entry_price, stoploss, side)
                session.set_trading_stop(symbol=symbol, side=side, stop_loss=stoploss, take_profit=tp)

                # Sending notification
                nto(my_position_entry_price, side, str(entry_hour))

                # Printing some information
                print("\n############  order is now being executed  ############\n")
                print(f"open price: {my_position_entry_price}")
                print(f"stop loss: {stoploss}")
                print(f"take profit: {tp}")
                print(f"side: {side}")
                print(f"{entry_hour}")
                break
            check_no += 1
            time.sleep(2)

       
        try:
            x = get_correct_index(session.my_position(symbol=symbol)['result'])
            my_position_entry_price = session.my_position(
                symbol=symbol)['result'][x]['entry_price']
        except:
            time.sleep(60)
            x = get_correct_index(session.my_position(symbol=symbol)['result'])
            my_position_entry_price = session.my_position(
                symbol=symbol)['result'][x]['entry_price']
        to_excel_entry = my_position_entry_price
         # Trade Zone
        while my_position_entry_price != 0:
            df = get3minutedata(symbol)
            time.sleep(2)    
            try:
                last_price = session.latest_information_for_symbol(
                    symbol=symbol)['result'][0]['index_price']
                my_position_entry_price = session.my_position(
                    symbol=symbol)['result'][x]['entry_price']
            except:
                time.sleep(60)
                last_price = session.latest_information_for_symbol(
                    symbol=symbol)['result'][0]['index_price']
                my_position_entry_price = session.my_position(
                    symbol=symbol)['result'][x]['entry_price']

        # sending notifications
        closed_pnl = calculate_pnl(qty, to_excel_entry, last_price, stoploss, tp)
        ntc(to_excel_entry, session.latest_information_for_symbol(symbol=symbol)['result'][0]['index_price'], closed_pnl, datetime.now().strftime("%H:%M:%S"))
        trade_id += 1
        print(f"\nTrade was closed\nPNL: {closed_pnl}")

try:
    run()
except Exception as e:
    ns("Closed", datetime.now().strftime("%H:%M:%S"))
    print(e)









