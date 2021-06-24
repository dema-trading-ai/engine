FROM python:3.9.1-slim-buster as base

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONIOENCODING=utf-8

RUN mkdir /usr/src/engine/
WORKDIR /usr/src/engine/

RUN apt-get update \
    && apt-get -y install --no-install-recommends curl build-essential \
    && apt-get clean \
    && pip install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*

COPY installation_helpers/* /tmp/
RUN chmod 777 /tmp/install_talib.sh
RUN cd /tmp && /tmp/install_talib.sh && rm -r /tmp/*ta-lib*
ENV LD_LIBRARY_PATH /usr/local/lib

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . .

WORKDIR /app

ENTRYPOINT ["python", "/usr/src/engine/main.py"]
