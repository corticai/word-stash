FROM amazon/aws-sam-cli-build-image-python3.8
WORKDIR /tempdir

COPY ./tests/requirements.tests.txt .
RUN pip install -r requirements.tests.txt

COPY . .
