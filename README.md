# DemaTrading.ai Engine

# Discord

Please join our Discord for updates, support, our community & more:
https://discord.gg/WXxjtNzjEx

## Running

### Requirements for running with Docker (recommended)

Running the Engine just takes a few simple things:

1. Docker installed on your system (https://docs.docker.com/get-docker/)
2. Some code editor (https://www.jetbrains.com/pycharm/)
3. Abillity to copy + paste and some motivation to figure things out.

### Requirements for running without Docker (alternative)

Running the Engine just takes a few simple things:

1. Have Python 3 installed on your system (https://www.python.org/downloads/)
2. Pip Running on your system (https://pip.pypa.io/en/stable/installing/)
3. Some code editor (https://www.jetbrains.com/pycharm/)
4. Install TA-Lib dependencies (see: https://github.com/mrjbq7/ta-lib Installation -> Dependencies)

#### Running without Docker

First run:

```
pip install -r requirements.txt
```

After installing, you can run the Engine:

```
python3 main.py
```

#### Running with Docker

First run:

```
docker build . -t dema-engine:alpha
```

To run the container:

```
docker run --rm dema-engine:alpha
```

To run the container with a volume (rebuilding not necessary on code changes)

```
docker run --rm -v "$(pwd):/engine" dema-engine:alpha
```

Note: do not forget '--rm' as your Docker will keep the container if you do, which is not necessary and will cause extreme increase in memory usage.

#### Using `make`

As the `docker` commands listed above are not so developer friendly, we added a `Makefile` to help you save some tears. You'll need to have `make` installed on your system, which is on most computers by default. If you have, you can run the docker commands as follows.

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

#### GitFlow

To keep features, versions and fixes organized, we will be using the following gitflow.
![Our gitflow](https://images.prismic.io/clubhouse/e02ba62c-26e6-4250-acff-1b2c93ecc789_image-32.png)

## Full Documentation

https://www.docs.DemaTrading.ai

## License

This project is licensed under AGPL-3.0 License. It is not allowed to use this project to run any live trading instances. This project is for strategy testing only, if you want to monetise your strategy you can contact us. We can also help you to optimise your strategy. Any questions regarding this project? Feel free to get in touch using the contact form at https://DemaTrading.ai.

#### New Features

> T.B.A.

#### Improvements

> T.B.A

#### Standard GitFlow

> T.B.A
