# ByBitBot

Bot executes trades based on trading strategy: **100EMA + PARABOLIC SAR + MACD**
It sets up stop loss and take profit prices by itself


Before running the project make sure to:

1. Create secrets.py file 

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


2. Install all requirements:
You will find them inside requirements.txt file

