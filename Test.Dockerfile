FROM python:3.9 as base

WORKDIR /app

COPY dist/main /bin/

ENTRYPOINT ["/bin/main"]