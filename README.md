[![Codacy Badge](https://app.codacy.com/project/badge/Grade/4eb3be6897544c2faa05ff80a3dfcf06)](https://www.codacy.com/gh/dema-trading-ai/engine/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dema-trading-ai/engine&amp;utm_campaign=Badge_Grade)
[![Build Status](https://img.shields.io/github/forks/dema-trading-ai/engine.svg)](https://github.com/dema-trading-ai/engine)
[![Build Status](https://img.shields.io/github/stars/dema-trading-ai/engine.svg)](https://github.com/dema-trading-ai/engine)
[![License](https://img.shields.io/github/license/dema-trading-ai/engine.svg)](https://github.com/dema-trading-ai/engine)
[![Test PR/Push](https://github.com/dema-trading-ai/engine/actions/workflows/PR-Push-test.yml/badge.svg?branch=development)](https://github.com/dema-trading-ai/engine/actions/workflows/PR-Push-test.yml)

<p align="center">
  <img src="https://github.com/dema-trading-ai/engine/raw/feat/update-readme/imgs/DemaTrading-text-transparant.png">
</p>

# Engine
The DemaTrading.ai Engine is an open source backtesting Engine for cryptocurrency trading as a 
part of [DemaTrading](https://dematrading.ai/). The Engine is completely written in the 
programming language Python. Some experience with Python makes this process easier, 
however with some effort this project should be runnable for everyone, no matter your experience with coding.

![Backtesting Results](https://github.com/dema-trading-ai/engine/raw/feat/update-readme/imgs/backtesting-results.png)

##### [Go to full documentation](https://docs.dematrading.ai)


# Discord

For any questions not covered by the documentation, or for further questions regarding the engine, 
trading, your own strategies, your algorithms, or just a chit chat with like-minded individuals, 
you are more than welcome join our Discord server, where we will facilitate whatever need you 
may have.

##### [Join Discord server](https://discord.gg/WXxjtNzjEx)


# Running
There are multiple ways to run our Backtesting Engine. For each way, the installation steps are outlined below.
We recommend using Docker to run the Backtesting Engine, but you can also use standard Python.

#### Installing Code Editor
To make your a life a lot easier during strategy development use a code editor such as [PyCharm](https://www.jetbrains.com/pycharm/) 
(recommended) or [VSCode](https://code.visualstudio.com/).


## Running with Docker (recommended)
If you want to run the engine using Docker, you need to install Docker using the steps described 
[here](https://docs.docker.com/get-docker/). After installing you need to run Docker in the 
background.

#### Docker Commands
To run the engine you have to open a terminal of choice and enter the commands described below. 
1. This command will initialize a directory containing all the necessary files for running the
engine and developing strategies:
```
docker run -t --rm -v "$(pwd):/usr/src/engine/output" dematrading/engine:stable init
```
> Note: if you are using Windows, please use Windows Powershell to perform this command.

2. To run a backtest use the following command:
```
docker-compose up
```


## Running with Python (alternative)
If you want to run the engine using Python, first you need to download Python 3.8.6 by clicking 
[this](https://www.python.org/downloads/release/python-386/) link. Furthermore, you will have to 
manually download this repository on your computer. This can be done by either downloading the 
repository as a .zip file or the recommended way which is cloning the repository 
using [Github Desktop](https://desktop.github.com/) (or something similar). For more information 
about cloning a repository see [this](https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/adding-and-cloning-repositories/cloning-and-forking-repositories-from-github-desktop) 
link. To use the engine you need TA-lib, which can be installed using the following steps that 
correspond to your operating system.

#### MacOS Installation
> Note: if you're device is running on the M1 Chip by Apple Silicon, please follow the 
installation instruction described in our [docs](https://docs.dematrading.ai/getting_started/installation/installation/#apple-silicon-m1-chip).

1. Install Homebrew (optional). This can be done by running the following command in your 
terminal:
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Install TA-lib library by running this command:
```
brew install ta-lib
```
OR if you you skipped Step 1. you can run this command (requires [Xcode12](https://developer.apple.com/download/)):
```
pip install ta-lib
```

#### Linux Installation
1. Download [ta-lib-0.4.0-src.tar.gz](http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz).

2. Run the following commands:
```
$ tar -xzf ta-lib-0.4.0-src.tar.gz
$ cd ta-lib/
$ ./configure --prefix=/usr
$ make
$ sudo make install
```

#### Windows Installation
1. Find your current operating system. This can be found in system settings (either 32-bit or 
64-bit)

2. Go to [this](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib) link and search the page for 
"ta-lib". 
- If you have a 64-bit operating system download: TA_Lib‑0.4.20‑cp38‑cp38‑win_amd64.whl 
- If you have a 32-bit operating system download: TA_Lib‑0.4.20‑cp38‑cp38‑win32.whl

3. Open a terminal (e.g. Windows Powershell) and change to the downloads folder: 
```
cd [PATH/TO/DOWNLOADS/FOLDER]
```

4. Install the TA-lib wheel by running this command:
```
pip install [TA_Lib-wheel].whl
```

### Running the Engine
1. Change to the engine directory by running this command:
```
cd [PATH/TO/ENGINE/DIRECTORY]
```

2. Install all other needed dependencies by running this command:
```
pip install -r requirements.txt
```

3. Run the engine by running this command:
```
python3 main.py
```


# Developing
To start developing your very own strategy, we suggest reading our [docs](https://docs.dematrading.ai/getting_started/strategies/strategyexamples/) 
for more information.
> To give you a headstart, we included a sample strategy which can be found in 
/resources/setup/strategies/my_strategy.py

If you want to create your own strategy just simply copy the sample strategy and change the name 
of the class to for example 'MyNewStrategy'. Then just change the config.json file in the engine 
directory accordingly to test this strategy:
```
"strategy-name": "MyNewStrategy"
```

For feature requests or suggestions, please write a message in our [Discord](https://discord.gg/WXxjtNzjEx) 
under #engine-support.


# License
This project is licensed under AGPL-3.0 License. It is not allowed to use this project to run any live trading instances. This project is for strategy testing only, if you want to monetise your strategy you can contact us. We can also help you to optimise your strategy. Any questions regarding this project? Feel free to get in touch using the contactform at https://DemaTrading.ai. 


