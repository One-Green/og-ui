FROM python:3.10.6-buster as run

ENV PYTHONUNBUFFERED TRUE
WORKDIR /app

COPY . /app
RUN pip install --upgrade pip  \
    && pip install --no-cache-dir pipenv \
    && pipenv install --system --deploy --clear \
    && pip uninstall pipenv virtualenv -y

CMD []
ENTRYPOINT []
