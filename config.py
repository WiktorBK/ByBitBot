
'''
This is a configuration file for ByBitBot
'''

# symbol to be traded
SYMBOL = 'ETHUSDT'

'''
interval to be used

eg: 3 -> 3 minutes,
    15 -> 15 minutes

'''

INTERVAL = '3'



'''
 quantity to be traded

 this will be amount of specified cryptocurrency (SYMBOL) to be bought every trade

 ! WARNING - do not use high values without testing out the program!

'''

QTY = 0.01


'''
in the file named 'secret.py' specify your bybit keys

go to your account and grab them from this link:
https://www.bybit.com/app/user/api-management

'''

from secret import api_key, api_secret
AKEY=api_key
ASECRET=api_secret