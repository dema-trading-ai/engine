# DemaTrading.ai Engine
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/4eb3be6897544c2faa05ff80a3dfcf06)](https://www.codacy.com/gh/dema-trading-ai/engine/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dema-trading-ai/engine&amp;utm_campaign=Badge_Grade)
[![Build Status](https://img.shields.io/github/forks/dema-trading-ai/engine.svg)](https://github.com/dema-trading-ai/engine)
[![Build Status](https://img.shields.io/github/stars/dema-trading-ai/engine.svg)](https://github.com/dema-trading-ai/engine)
[![License](https://img.shields.io/github/license/dema-trading-ai/engine.svg)](https://github.com/dema-trading-ai/engine)
[![Test PR/Push](https://github.com/dema-trading-ai/engine/actions/workflows/PR-Push-test.yml/badge.svg)](https://github.com/dema-trading-ai/engine/actions/workflows/PR-Push-test.yml)

# Discord

Please join our Discord for updates, support, our community & more:
https://discord.gg/WXxjtNzjEx

# Running

## Requirements for running with Docker (recommended)

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

## Running without Docker

First run:

```
pip install -r requirements.txt
```

After installing, you can run the Engine:

```
python3 main.py
```

## Running with Docker

First run:

```
docker build . -t dema-engine:alpha
```

To run the container:

```
docker run --rm dema-engine:alpha
```

To run the container with a volume (rebuilding not necessary on code changes):

```
docker run --rm -v "$(pwd):/engine" dema-engine:alpha
```

Note: do not forget '--rm' as your Docker will keep the container if you do not. Keeping the container is unnecessary and will cause an extreme increase in memory usage.

## Using `make`

As the `docker` commands listed above are not so developer friendly, we added a `Makefile` to help you save some tears. You will need to have `make` installed on your system (check using `make --version`), which is installed on most computers by default. If you do not have `make` installed, run `brew install make` (homebrew needed), `sudo apt install make` or `choco install make` (chocolately needed) for MacOS, Linux or Windows, respectively.

To build the image:

```
make build
```

To run the container:

```
make run
```

To run on volume:

```
make runv
```

To build and run:

```
make
```

## Developing
For feature requests or suggestions, please create an issue. If you want to work on a certain functionality, please create an issue first.

## Full Documentation

https://docs.DemaTrading.ai

## License

This project is licensed under AGPL-3.0 License. It is not allowed to use this project to run any live trading instances. This project is for strategy testing only, if you want to monetise your strategy you can contact us. We can also help you to optimise your strategy. Any questions regarding this project? Feel free to get in touch using the contactform at https://DemaTrading.ai. 


