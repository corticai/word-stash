FROM python:3.9-slim
WORKDIR data-impleter
COPY ./tests/requirements.tests.txt .
RUN pip install -r requirements.tests.txt
COPY . . 