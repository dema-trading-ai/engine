# Developing a strategy
On this page you will learn how to get started with developing your very own strategy. To give you a headstart, we included a sample strategy which can be found in ``/strategies/my_strategy.py``. 

## Sample strategy
How does our sample strategy work? We will guide you through the process. The sample can be found in ``/strategies/my_strategy.py``. 

### Generate indicators
To be able to base our buy / sell signal on indicators, we need to generate these strategies. 

For this strategy we decided we want to use RSI and EMA indicators to trigger buys/sells. We can make the calculated value available to the buy/sell methods by adding it to the dataframe. Like this for example: 
``dataframe['rsi'] = ta.RSI(dataframe)``

!!! attention
    Setting this to another value than the maximum span of candles used will result in distorted results or errors.

### Buy signal
In our buy signal, we set some conditions for our signal. In our implementation, the pair wil only be bought when all of the following conditions are true.
```python
current_candle['rsi'] < 30
current_candle['ema5'] < current_candle['ema21']
current_candle['volume'] > 0
```

### Sell signal
In our sell signal, we set some conditions for our signal. In our implementation, the pair wil only be sold when all of the following conditions are true. Beside the sell signal, positions can be closed using the [Stop Loss](#Stop_loss) or [Return on Investment](#ROI) configurations in the ``config.json`` file.
```python
current_candle['rsi'] > 70
current_candle['volume'] > 0
```

### Minimum candles 
On the top of ``my_strategy.py``, ``min_candles`` is defined. This is used as an offset for the amount of candles needed to calculate the biggest indicator. In our case, SMA(21) needs atleast 21 candles to work properly. Therefore, we set ``min_candles`` to 21. 

### Configuration
In the ``config.json`` file you will find all necessary and important configuration options. 
#### ROI
#### Stop loss

## Getting started
### Finding indicators
### Configuring indicators
### Using indicators in sell/buy signal
### Configuring Stoploss / Return On Investment

Play with Technical Indicators on TradingView
Find nice Technical Indicators
Look at for available indicators in TA-lib http://mrjbq7.github.io/ta-lib/funcs.html
Implement indicators in indicator method
Implement populated indicators in buy / sell signal
Make the indicators work better
Combining with SL / ROI

## Extra information
If you have trouble understanding our engine, the following resources could be useful for increasing your python skills.