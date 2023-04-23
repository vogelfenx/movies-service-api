FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat
WORKDIR /etl
COPY ./etl/requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir
COPY ./etl .
COPY ./Docker_settings/etl/*.sh .
RUN ["chmod", "+x", "commands.sh"]
RUN ["chmod", "+x", "wait_services_up.sh"]
ENTRYPOINT ["./commands.sh"]