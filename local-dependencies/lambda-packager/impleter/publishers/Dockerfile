# FROM python:3.8-slim-buster
FROM public.ecr.aws/lambda/python:3.8
WORKDIR impleter
COPY impleter/publishers/src/requirements.txt .
COPY impleter/publishers/src/ src
COPY impleter/publishers/scripts/create_and_upload_packages.sh .
RUN yum install -y zip
RUN pip install awscli
RUN chmod +x create_and_upload_packages.sh
ENTRYPOINT [ "bash", "create_and_upload_packages.sh" ]