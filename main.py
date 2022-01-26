from hmac import new
import pandas as pd
import time
import calendar
from pandas.core.frame import DataFrame 
from pybit import HTTP
from secrets import apikey, apisecret
from datetime import datetime
from ta.trend import EMAIndicator, PSARIndicator, macd_diff
from excel import to_excel
from notifications import nlc, ns, ntc, nto, nrc


#############
symbol='ETHUSDT'
tick_interval = '3'
qty=0.01
#############


now = datetime.utcnow()
unixtime = calendar.timegm(now.utctimetuple())
since = unixtime - 60  * 60 * 3*2

# Opening bybit session
session = HTTP(
    "https://api.bybit.com",
    api_key = apikey,
    api_secret = apisecret,
    request_timeout= 60
)

# notification
ns("Started",  datetime.now().strftime("%H:%M:%S"))

def get3minutedata(symbol): 
    # Get Data
    try:
        data = session.query_kline(
            symbol= symbol, 
            interval = '3',
            **{'from':since}
        )['result']
    except:
        print("Lost Connection")
        print("Reconnecting...")
        nlc(datetime.now().strftime("%H:%M:%S"))
        time.sleep(60)
        data = session.query_kline(
            symbol= symbol, 
            interval = '3',
            **{'from':since}
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
    df['pSAR_down'] = PSARIndicator(df['High'], df['Low'], df['Close']).psar_down()
    df['pSAR_up'] = PSARIndicator(df['High'], df['Low'], df['Close']).psar_up()


    # Checking different PSAR conditions
    if pd.isna(df['pSAR_down'][-2]) == False and pd.isna(df['pSAR_down'][-1]) == True or pd.isna(df['pSAR_down'][-3]) == False and pd.isna(df['pSAR_down'][-2]) == True \
    or pd.isna(df['pSAR_down'][-4]) == False and pd.isna(df['pSAR_down'][-3]) == True:
        return "Buy"
    elif  pd.isna(df['pSAR_down'][-2]) == True and pd.isna(df['pSAR_down'][-1]) == False or pd.isna(df['pSAR_down'][-3]) == True and pd.isna(df['pSAR_down'][-2]) == False \
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


def calculate_pnl(qty, side, entry_price, hitby, sl, tp):
    entry_size = qty * entry_price
    entry_fee = entry_size * 0.00075
    if hitby == "sl" and side == "Sell":
        close_size = sl * qty
        close_fee = close_size * 0.00075
        pnl = (entry_size - close_size - close_fee - entry_fee)
    elif hitby == "sl" and side == "Buy":
        close_size = sl * qty
        close_fee = close_size * 0.00075
        pnl = (entry_size - close_size + close_fee + entry_fee) * -1
    elif hitby == "tp" and side == "Buy":
        close_size = tp * qty
        close_fee = close_size * 0.00075
        pnl = (close_size - entry_size - close_fee - entry_fee)
    elif hitby == "tp" and side == "Sell":
        close_size = tp * qty
        close_fee = close_size * 0.00075
        pnl = (entry_size - close_size - close_fee - entry_fee)
    return pnl


def aboutToHitTP(entry_price, tp, last_price):
    diff = abs(entry_price - tp)
    onefourth = 0.33 * diff
    last_price = float(last_price)
    tp = float(tp)
    if tp < entry_price:
        if last_price <= onefourth + tp:
            return True
        else:
            return False
    elif tp > entry_price:
        if last_price >= tp - onefourth:
            return True
        else:
            return False


def setnewstoploss(sl, entry_price, side):
    diff = abs(entry_price - sl)
    new_diff = diff/2
    if sl > entry_price:
        new_sl = entry_price + new_diff    
    elif sl < entry_price:
        new_sl = entry_price - new_diff

    session.set_trading_stop(symbol = symbol, stop_loss = sl, side = side)



def run():

    # Starting main loop
    trade_id = 0
    check_no = 1
    while True:

        # This is executed at the begining and after every trade
        my_position_entry_price = session.my_position(symbol=symbol)['result'][0]['entry_price']
        print("\n\n### Trading Bot is now checking for signals ###\n")
        print("Trading Strategy: Parabolic Sar + MACD + 100EMA")
        print("......\n")

        # Checking data every 2 seconds
        while True:

            df = get3minutedata(symbol)
            print(check_for_psar_signal(df), check_for_ema_signal(df), check_for_macd_signal(df), check_no)

            # Checking if the signals are the same
            if check_for_psar_signal(df) == check_for_ema_signal(df) == check_for_macd_signal(df):

                # If signals are correct postion opens and then we break out of the loop
                side = check_for_ema_signal(df)
                stoploss = psar_price(df)
                open_price = df['Close'][-1]
                now = datetime.now()
                entry_hour = now.strftime("%H:%M:%S")
                place_active_order(qty, side)
                my_position_entry_price = session.my_position(symbol=symbol)['result'][0]['entry_price'] 
                tp = calculate_takeprofit(my_position_entry_price, stoploss, side)
                session.set_trading_stop(symbol = symbol, side = side, stop_loss = stoploss, take_profit = tp)

                # Sending notification
                nto(my_position_entry_price, side, str(entry_hour))

                # Printing some information 
                print("\n############  order is now being executed  ############\n")
                print(f"open price: {my_position_entry_price}")
                print(f"stop loss: {stoploss}")
                print(f"side: {side}")
                print(f"take profit: {tp}")
                print(datetime.now())

                trade_id+=1
                break

            check_no += 1
            time.sleep(2)

        # This is trade zone where we wait for the trade to end
        sl_changed = False
        sl_at_entry = False
        while my_position_entry_price != 0:
            time.sleep(2)
            last_price = session.latest_information_for_symbol(symbol = symbol)['result'][0]['index_price']
            my_position_entry_price = session.my_position(symbol=symbol)['result'][0]['entry_price']
            tp_diff = abs(tp - float(my_position_entry_price))
            tp_diff_part = tp_diff * 0.08
            distance_fromtp = abs(tp - float(last_price))

            # Moving stop loss according to price conditions
            if aboutToHitTP(my_position_entry_price, tp, last_price) and sl_changed == False:
                print("Stoploss has been moved")
                setnewstoploss(stoploss, my_position_entry_price, side)
                sl_changed = True
            if sl_at_entry == False and distance_fromtp <= tp_diff_part:
                session.set_trading_stop(symbol = symbol, stop_loss = float(my_position_entry_price), side = side)
                sl_at_entry = True

        # sending notifications and uploading to excel
        closed_pnl = session.closed_profit_and_loss(symbol = symbol)['result']['data'][0]['closed_pnl']
        to_excel(trade_id, my_position_entry_price, side, qty, entry_hour, datetime.now().strftime("%H:%M:%S"), closed_pnl)
        ntc(my_position_entry_price, session.latest_information_for_symbol(symbol = symbol)['result'][0]['index_price'], datetime.now().strftime("%H:%M:%S"))

try:
    run()
except Exception as e:
    ns("Closed", datetime.now().strftime("%H:%M:%S")) 
    print(e)





