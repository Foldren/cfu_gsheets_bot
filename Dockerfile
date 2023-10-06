FROM python:3.11-alpine
WORKDIR /home
RUN apk update
COPY /source /source
COPY ./requirements.txt /source/requirements.txt
WORKDIR /source
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /source/requirements.txt