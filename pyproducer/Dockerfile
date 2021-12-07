FROM python:3.9-alpine

ARG CONSUMER_GROUP "default"

ENV ENV_CONSUMER_GROUP ${CONSUMER_GROUP}

WORKDIR /app

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY ./app.py .

CMD ["sh", "-c", "python app.py ${ENV_CONSUMER_GROUP}"]