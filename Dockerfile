FROM python:3.11-alpine3.18

ENV PYTHONUNBUFFERED=1

WORKDIR /django-app

COPY requirements.txt requirements.txt

EXPOSE 8000

RUN apk add postgresql-client build-base postgresql-dev

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY megano .

COPY diploma-frontend/dist/diploma-frontend-0.6.tar.gz diploma-frontend-0.6.tar.gz

RUN pip install diploma-frontend-0.6.tar.gz

RUN python manage.py collectstatic --no-input

