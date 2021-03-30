# How we can help you with monetisation

DemaTrading.ai was founded with the idea to be the perfect partner for anyone in, or interesting getting in, the beautiful world of algorithmic trading.
We help traders to automate, optimise and monetise their trading strategies. No experience in trading? We can help you with your learning journey.

## Calculation example

An investor can put funds into your algorithm, trading with it, following this, you'll be able to earn money! Here's an example to show you how much you can earn:

1.000.000 in total funds (can be via multiple bots).
A fee of 0.01% per trade, from which the algorithm supplier gets 60%.
This will be multiplied by 2 (1 buy and 1 sale per day). With 30 trades per month on average this can easily average the following:

1.000.000 x 0.0001 x 0.6 x 2 x 30 = 3600 per month (this is the full amount the algorithm supplier makes per month).

Under the condition that the bot trades twice per day, the algorithm supplier can make 7200 per month etc.

Disclaimer: the fee in the algorithm needs to be 0.0025 (2.5%)

## For beginners

### Configuration

In the ``config.json`` file you will find all necessary and important configuration options.

#### ROI

The ROI table in the configuration is used to sell at a certain percentage of profit after a defined time. The `keys` in the dictionary are in minutes, the `values` are the percentages. Keys should always be an `int` with double quotes. Value could be an `int` or a `float`.

```json
   "roi": {
     "0": 5,
     "60": 4,
     "120": 3.5
   }
```

This configuration means positions will always be closed if the profit is higher than 5%. After an hour (60 minutes) the position will automatically be closed if the profit is higher than 4%.

#### Stop loss

The stoploss (SL) function is to prevent extreme loses. The SL value in the configuration file could be a `float` or an `int`.

```json
   "stoploss": "-0.5",
```

This configuration means positions will always be closed if the profit is lower than -0.5%.

### Getting started

Now you've seen how we configured all the basic settings and buy/sell signals. From now on, you can start working on **your very own trading algorithms**. More information regarding this can be found on the strategies page.

## For manual traders

If you have a strategy but you've done it manually, you're uncertain as to how to automate it yourself via strategies and automated trading, we can help you! We can automate it for you, depending on your strategy, and how effective it is and so forth!

## For algo traders

For algorithm traders, and you've developed a strategy that works, there are a few steps that you'd have to go through, but don't worry! They're not complicated what-so-ever.

1. Sign contract: you sign a contract with us, which will be provided after a brief conversation with us (follows the local laws and the European laws; we're registered in Amsterdam).
2. Test and validate: we test the algorithm you provide us and test it, see whether it is valid or not and whether it is a strategy all parties can profit off of.
3. Optimize: we or you - in conjunction with us - optimize the algorithm, ensure it can work on our platform without fail nor error.
4. Sandbox period: in the sandbox period, we dry-run the algorithm, ensuring that it will actually function and that it will be profitable for everyone involved.
5. Going live: the final step. Your algorithm is now live! Time to earn some money!

After these steps, you'll be paid on a monthly basis by us based on how much investors trade with your algorithm via the platform! Via the calculation example, you can see how much you'll be able to make on a monthly basis!