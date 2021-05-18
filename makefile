all: build run

help:
	docker run --rm dema-engine:alpha main.py --help

build:
	docker build . -t dema-engine:alpha

update:
	docker pull dema-engine:alpha

run:
	docker run --rm -v "$(shell pwd):/usr/src/engine/" dema-engine:alpha

runv:
	docker run --rm -v "$(shell pwd):/usr/src/engine/" dema-engine:alpha
