
# BybitBot

ByBitBot is a program built with python. It's main purpose is to provide great returns on cryptocurrency investements. Bot is fully automated and doesn't require human interference.

## How does it work?

ByBitBot works on the basis of a popular online cryptocurrency exchange - **ByBit**. Program executes trades based on trading strategy: **100EMA + PARABOLIC SAR + MACD**. This strategy consists of 3 different technical indicators which are calculated by python-ta library. Whenever strategy indicates good oportunity, program buys certain amount of crypto and sets stoploss and take-profit prices by itself.

## Installation

- Create virutal environment
- `git clone https://github.com/WiktorBK/ByBitBot.git`
- `pip install -r requirements.txt`

Configure your bot inside `config.py` file. Remember to create `secret.py` file and specify your bybit keys.

## Usage

After installing the program enter this command:

`run.py`

Output received every 3 seconds:

~~~
Current signals:
MACD: NO SIGNAL; PSAR: NO SIGNAL; EMA: Buy
Last price of ETHUSDT: 1821.43
~~~

When trade opens:
~~~
Position has been opened!
Side: Buy
Last Price: 1821.43
~~~

During Trade:

```
Waiting for trade to end
```

## Authors

- [@Wiktor Bożek](https://www.github.com/WiktorBK)

## License

[MIT](https://github.com/WiktorBK/ByBitBot/blob/master/LICENSE)
