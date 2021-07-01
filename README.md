# DemaTrading.ai Engine
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/4eb3be6897544c2faa05ff80a3dfcf06)](https://www.codacy.com/gh/dema-trading-ai/engine/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dema-trading-ai/engine&amp;utm_campaign=Badge_Grade)
[![Build Status](https://img.shields.io/github/forks/dema-trading-ai/engine.svg)](https://github.com/dema-trading-ai/engine)
[![Build Status](https://img.shields.io/github/stars/dema-trading-ai/engine.svg)](https://github.com/dema-trading-ai/engine)
[![License](https://img.shields.io/github/license/dema-trading-ai/engine.svg)](https://github.com/dema-trading-ai/engine)
[![Test PR/Push](https://github.com/dema-trading-ai/engine/actions/workflows/PR-Push-test.yml/badge.svg?branch=development)](https://github.com/dema-trading-ai/engine/actions/workflows/PR-Push-test.yml)

The DemaTrading.ai Engine is an open source backtesting Engine for cryptocurrency trading as a 
part of [DemaTrading](https://dematrading.ai/). The Engine is completely written in the 
programming language Python. Some experience with Python makes this process easier, 
however with some effort this project should be runnable for everyone, no matter your experience with coding.

![Backtesting Results](./imgs/backtesting_results.png?raw=true "Backtesting Results")
![Coin Insights](./imgs/coin_insights.png?raw=true "Coin Insights")

##### [Go to full documentation](https://docs.dematrading.ai)


## Discord

For any questions not covered by the documentation, or for further questions regarding the engine, 
trading, your own strategies, your algorithms, or just a chit chat with like-minded individuals, 
you are more than welcome join our Discord server, where we will facilitate whatever need you 
may have.

##### [Join Discord server](https://discord.gg/WXxjtNzjEx)


## Installing
There are multiple ways to run our Backtesting Engine. For each way, the installation steps are outlined below.
We recommend using Docker to run the Backtesting Engine, but you can also use standard Python.

!! Attention: Running without Docker? You will have to manually download this repository on your computer. 
This can be done by either downloading the repository as a .zip file or the recommended way which is cloning the repository 
using [Github Desktop](https://desktop.github.com/) (or something similar). For more information about cloning a repository see 
[this](https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/adding-and-cloning-repositories/cloning-and-forking-repositories-from-github-desktop) link.


### Installing Code Editor
To make your a life a lot easier during strategy development use a code editor such as [PyCharm](https://www.jetbrains.com/pycharm/) 
(recommended) or [VSCode](https://code.visualstudio.com/).


### Installing Docker (recommended)
If you want to run the engine using Docker, you need to install Docker using the steps described [here](https://docs.docker.com/get-docker/).


### Installing Python (alternative)
If you want to run the engine using Python, you need the follow these steps.
#### MacOS / Linux
1. Installing Python 3.9.6, which can be done [here](https://www.python.org/downloads/).
2. Installing Homebrew (recommended). This can be done by copying the following line into your terminal app:
```
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
3. Download and install [Xcode12](https://developer.apple.com/download/)
4. 

### Requirements for running with Docker (recommended)

Running the Engine just takes a few simple things:

1. Docker installed on your system (https://docs.docker.com/get-docker/)
2. Some code editor (https://www.jetbrains.com/pycharm/)
3. Abillity to copy + paste and some motivation to figure things out.

## Requirements for running without Docker (alternative)

Running the Engine just takes a few simple things:

1. Have Python 3 installed on your system (https://www.python.org/downloads/)
2. Pip Running on your system (https://pip.pypa.io/en/stable/installing/)
3. Some code editor (https://www.jetbrains.com/pycharm/)
4. Install TA-Lib dependencies (see: https://github.com/mrjbq7/ta-lib Installation -> Dependencies)


## Running with Docker

To initialize a directory for running our engine, run the command below. Note: this command needs to be run in an empty directory. 
This command will generate all necessary files for running the engine and developing strategies.

```
docker run -t --rm -v "$(pwd):/usr/src/engine/output" dematrading/engine:stable init
```

> Note: if you are using Windows, please use powershell to perform this command.


To run a backtest:

```
docker-compose up
``` 


## Running without Docker

First run:

```
pip install -r requirements.txt
```

After installing, you can run the Engine:

```
python3 main.py
```

## Developing
For feature requests or suggestions, please create an issue. If you want to work on a certain functionality, please create an issue first.

## Full Documentation

https://docs.DemaTrading.ai

## License

This project is licensed under AGPL-3.0 License. It is not allowed to use this project to run any live trading instances. This project is for strategy testing only, if you want to monetise your strategy you can contact us. We can also help you to optimise your strategy. Any questions regarding this project? Feel free to get in touch using the contactform at https://DemaTrading.ai. 


