# test
FROM python:3.10.6-slim-buster as builder
WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt update && apt install git -y
RUN pip3 --no-cache-dir install --upgrade pip
RUN pip3 --no-cache-dir install -r /app/requirements.txt --target=/py-dependencies --no-dependencies

FROM python:3.10.6-slim-buster as run

ENV PYTHONUNBUFFERED TRUE
WORKDIR /app

COPY . /app
COPY --from=builder /py-dependencies /py-dependencies
ENV PYTHONPATH="${PYTHONPATH}:/py-dependencies"

CMD []
ENTRYPOINT []
