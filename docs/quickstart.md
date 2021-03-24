# Running
### Requirements for running with Docker (recommended)
Running the Engine just takes a few simple things:
1. Have Docker installed on your system ([click here to download Docker](https://docs.docker.com/get-docker/))
2. A code editor such as [Pycharm](https://www.jetbrains.com/pycharm/) or [VSCode](https://code.visualstudio.com).
3. Abillity to copy + paste and some motivation to figure things out. 

### Requirements for running without Docker (alternative)
Running the Engine just takes a few simple things:
1. Have Python 3 installed ([click here to download Python](https://www.python.org/downloads/))
2. Have pip installed (Pip should be installed automatically on any version of Python that is 2.7 or above. If not installed on your system [click here!](https://pip.pypa.io/en/stable/installing/)).
3. A code editor such as [Pycharm](https://www.jetbrains.com/pycharm/) or [VSCode](https://code.visualstudio.com).
4. Install the TA-Lib dependencies ([follow the instructions given underneath the dependencies header](https://github.com/mrjbq7/ta-lib)).
5. Have this repository cloned on your computer. 

### Using `make`

As the docker commands listed above are not so developer friendly, we added a Makefile to help you save some tears. You'll need to have `make` installed on your system (check using `make --version`), which is on most computers by default. If you don't, run `brew install make` (homebrew needed), `sudo apt install make` or `choco install make` (chocolately needed) for MacOS, Linux or Windows, respectively.

To build the image:

`make build`

To run the container:

`make run`

To run on volume:

`make runv`

To build and run:

`make`

***
## Running the Engine.

### Running without Docker

First run:

`pip install -r requirements.txt`

After installing, you can run the backtesting module:

`python3 main.py`

### Running with Docker (Docker is a must if using an Apple system with the Apple Silicon M1 chip or else it does not work).

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
