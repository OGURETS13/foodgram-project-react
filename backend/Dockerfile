FROM --platform=linux/amd64 python:3.7-slim

RUN mkdir /app

COPY requirements.txt /app

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2
RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY ./ /app

WORKDIR /app

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000" ]