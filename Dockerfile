FROM python:3.11-alpine
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY ./source .
CMD ["python", "bot.py"]
