### What is ByBitBot?

ByBitBot is a program built with python. It's main purpose is to provide great returns on cryptocurrency investements.
Bot is fully automated and doesn't require human interference.

### How does it work?

ByBitBot works on the basis of a popular online cryptocurrency exchange - ByBit.
Program executes trades based on trading strategy: **100EMA + PARABOLIC SAR + MACD**.
This strategy consists of 3 different technical indicators which are calculated by **python-ta** library.
Whenever strategy indicates good oportunity, program buys certain amount of crypto and sets stoploss and take-profit prices by itself.
Bot sends notifications to your phone using **pushbullet** app simultaneously.
 
 


Before running the project make sure to:

- Install all requirements:
You will find them inside requirements.txt file

- create secrets.py file: 

```
# BYBIT
apikey = "apikey_from_bybit"
apisecret = "apisecret_from_bybit"

# MAIL
user = "email_adress"
password = "password"  
# in order to get password visit this URL https://myaccount.google.com/u/1/security. Activate 2-step verification and generate app password.

# PUSHUBULLET
accesstoken = "my_accesstoken_from_pushbullet" 
# create an account on pushbullet and install the app on your phone to get notifications about trades.
```


