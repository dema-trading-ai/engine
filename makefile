all: build run

build: 
	docker build . -t dema-engine:alpha

run:
	docker run --rm dema-engine:alpha

runv: 
	docker run --rm -v "$(shell pwd):/engine" dema-engine:alpha
