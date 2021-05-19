# syntax=docker/dockerfile:1
FROM python:3.8-slim
WORKDIR /code
ENV FLASK_APP=ui_web_server.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["flask", "run"]