FROM python:3.9.1-slim-buster as base

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONIOENCODING=utf-8

RUN mkdir engine/
WORKDIR engine/

RUN apt-get update \
    && apt-get -y install curl build-essential \
    && apt-get clean \
    && pip install --upgrade pip

COPY installation_helpers/* /tmp/
RUN chmod 777 /tmp/install_talib.sh
RUN cd /tmp && /tmp/install_talib.sh && rm -r /tmp/*ta-lib*
ENV LD_LIBRARY_PATH /usr/local/lib

COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["main.py"]