FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN echo $(ls)
COPY ./docker-scripts/entrypoint.sh entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./docker-scripts/django/django.sh django.sh
RUN chmod +x /django.sh

COPY ./docker-scripts/django/celery.sh celery.sh
RUN chmod +x /celery.sh

# Allows docker to cache installed dependencies between builds
COPY ./src/django/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Adds our application code to the image

WORKDIR /code


ENTRYPOINT ["/entrypoint.sh"]

