FROM python:3.11

ENV PYTHONUNBUFFERED=1

WORKDIR /django-app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY diploma-frontend/dist/diploma-frontend-0.6.tar.gz diploma-frontend-0.6.tar.gz

RUN pip install diploma-frontend-0.6.tar.gz

COPY megano .