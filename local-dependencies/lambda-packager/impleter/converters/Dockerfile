# FROM python:3.8-slim-buster
FROM public.ecr.aws/lambda/python:3.8
WORKDIR impleter
COPY impleter/converters/src/requirements.txt .
COPY impleter/converters/src/ src
COPY impleter/converters/scripts/create_and_upload_packages.sh .
# RUN apt-get -y update
# # Upgrade already installed packages:
# RUN apt-get -y upgrade
# # Install a new package:
# RUN apt-get -y install zip
RUN yum install -y zip
RUN pip install awscli
RUN chmod +x create_and_upload_packages.sh
ENTRYPOINT [ "bash", "create_and_upload_packages.sh" ]