FROM python:3.9-slim

WORKDIR /usr/src/selenium-bots
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/usr/src/selenium-bots
