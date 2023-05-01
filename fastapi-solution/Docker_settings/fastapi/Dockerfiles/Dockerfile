FROM python:3.10

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /opt/app

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir

COPY ./Docker_settings/fastapi/run_gunicorn.sh run_gunicorn.sh
COPY src src
WORKDIR /opt/app/src

ENTRYPOINT ["/bin/bash", "../run_gunicorn.sh"]
