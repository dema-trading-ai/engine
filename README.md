# dema-backtesting-module

## Running
### Requirements for running without Docker
Running this backtesting engine just takes a quite simple steps if you have the right things configured. Things you need:
1. Python 3 installed on your system
2. Pip Running on your system (https://pip.pypa.io/en/stable/installing/)
3. Some code editor (PyCharm Community or Visual Studio Code Community works fine)
4. Very very little knowlegde about Python

### Requirements for running with Docker
1. Docker installed on your system (https://docs.docker.com/get-docker/)
2. Some code editor (PyCharm Community or Visual Studio Code Community works fine)
3. Very very little knowlegde about Python


#### Running without Docker
First run:
```` 
pip install -r requirements.txt
````

After installing, you can run the backtesting module:
````
python3 main.py
````

#### Running with Docker
First run:
```` 
docker build . -t dema-engine:alpha
````

To run the container: 
````
docker run --rm dema-engine:alpha
````

Note: do not forget '--rm' as your Docker will keep the container if you do, which is not necessary and will cause extreme increase in memory usage.
## Developing
#### GitFlow
To keep features, versions and fixes organized, we will be using the following gitflow.
![Our gitflow](https://images.prismic.io/clubhouse/e02ba62c-26e6-4250-acff-1b2c93ecc789_image-32.png)

#### New Features
> T.B.A.

#### Improvements
> T.B.A

#### Standard GitFlow
> T.B.A

## License
This project is licensed under AGPL-3.0 License. It is not allowed to use this project to run any live trading instances. This project is for strategy testing only, if you want to monetise your strategy you can contact us. We can also help you to optimise your strategy. Any questions regarding this project? Feel free to get in touch using the contactform at https://DemaTrading.ai. 
