FROM python:3.8.5

WORKDIR /code
COPY requirements.txt /code
COPY . /code
RUN python3 -m pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir
CMD gunicorn api_yamdb.wsgi:application --bind 0.0.0.0:8000