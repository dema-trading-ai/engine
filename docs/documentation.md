# DemaTrading.ai backtesting engine.

[![Build Status](https://img.shields.io/github/forks/dema-trading-ai/engine.svg)](https://github.com/dema-trading-ai/engine)
[![Build Status](https://img.shields.io/github/stars/dema-trading-ai/engine.svg)](https://github.com/dema-trading-ai/engine)
[![License](https://img.shields.io/github/license/dema-trading-ai/engine.svg)](https://github.com/dema-trading-ai/engine)

<!-- Place this tag where you want the button to render. -->
<a class="github-button" href="https://github.com/dema-trading-ai/engine" data-icon="octicon-star" data-size="large" aria-label="Star dema-trading-ai/engine on GitHub">Star</a>
<!-- Place this tag where you want the button to render. -->
<a class="github-button" href="https://github.com/dema-trading-ai/engine/fork" data-icon="octicon-repo-forked" data-size="large" aria-label="Fork dema-trading-ai/engine on GitHub">Fork</a>
<!-- Place this tag where you want the button to render. -->
<a class="github-button" href="https://github.com/dema-trading-ai/engine/archive/main.zip" data-icon="octicon-cloud-download" data-size="large" aria-label="Clone dema-trading-ai/engine on GitHub">Download</a>

<!-- Place this tag where you want the button to render. -->
<a class="github-button" href="https://github.com/dema-trading-ai" data-size="large" aria-label="Follow @dema-trading-ai on GitHub">Follow @dema-trading-ai</a>

***

# Introduction

The DEMA-trading engine is an open source backtesting engine for trading as a part of the algorithm trading firm [DemaTrading](https://DemaTrading.ai). The engine is completely made with the programming language Python ([click here to download Python](https://www.python.org/downloads/)).

`A small bit of Python knowledge is recommended! However, there is no need to be extremely proficient at all!`

***

## Requirements

Running the backtesting engine is simple and can be done by anyone! The installation (without Docker) itself can be done within a few seconds by following the following steps:

1. Have Python 3 installed ([click here to download Python](https://www.python.org/downloads/))
2. Have pip installed (Pip should be installed automatically on any version of Python that is 2.7 or above. If not installed on your system [click here!](https://pip.pypa.io/en/stable/installing/)).
3. A code editor such as [Pycharm](https://www.jetbrains.com/pycharm/) or [VSCode](https://code.visualstudio.com).
4. Install the TA-Lib dependencies ([follow the instructions given underneath the dependencies header](https://github.com/mrjbq7/ta-lib)).
5. As previously mentioned, a tiny bit of Python knowledge!

## Requirements (with Docker)

Docker is an open platform for developing, shipping, and running applications. Docker enables you to separate your applications from your infrastructure so you can deliver software quickly. By using Docker there's a decrease in the delay of writing your code and testing/applying it in production.

1. Have Docker installed on your system ([click here to download Docker](https://docs.docker.com/get-docker/))
2. A code editor such as [Pycharm](https://www.jetbrains.com/pycharm/) or [VSCode](https://code.visualstudio.com).
3. As previously mentioned, a tiny bit of Python knowledge!

***

## Running the engine.

### Running without Docker

First run:

`pip install -r requirements.txt`

After installing, you can run the backtesting module:

`python3 main.py`

### Running with Docker (Docker is a must if using an Apple system with the Apple Silicon M1 chip or else it won't work).

First run:

`docker build . -t dema-engine:alpha`

To run the container:

`docker run --rm dema-engine:alpha`

Note: do not forget '--rm' as your Docker will keep the container if you do, which is not necessary and will cause extreme increase in memory usage.

### Apple Silicon M1 Chip

With the new M1 Chip by Apple Silicon, there are several compatibility issues with the packages required. While Docker works; TA-Lib, Pandas, and even Numpy are not compatible with the chip as of yet. The M1 Chip operates with ARM rather than x86, causing issues with regards to these Python packages. This is not something we are able to fix as it's on the behalf of the creators behind these packages and Apple itself, however, there are a few solutions that might help you or make it work on your Apple M1 machine.

1. Open your Terminal application with Rosetta 2 and then run the script.
2. You're ready to go!

If it doesn't work with Rosetta, don't worry! There's another solution that can be offered. Just follow the following steps:

1. Download [Xcode12](https://developer.apple.com/download/)
2. Install [Miniforge](https://github.com/conda-forge/miniforge)
3. Create a Condo environment (don't forget to start up a new .zsh session after having installed Miniforge.)
4. Use the following lines of code:
`conda create --name mytf`
`conda activate mytf`
`conda install -y python==3.8.6`
`conda install -y pandas TA-Lib`
5. You should be ready to go!
