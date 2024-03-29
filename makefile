all: build run

help:
	docker run --rm dema-engine:alpha main.py --help

build:
	docker build . -t dema-engine:alpha

run:
	docker run --rm -t -v "$(shell pwd):/usr/src/engine/" dema-engine:alpha

runv:
	docker run --rm -t -v "$(shell pwd):/usr/src/engine/" dema-engine:alpha
