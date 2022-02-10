#!/bin/sh
base_name=$1
env=$2
aws s3 rm --recursive s3://$base_name-converters-$env-backup-bucket
aws s3 rm --recursive s3://$base_name-lambda-packages-bucket
aws s3 rm --recursive s3://$base_name-parsers-$env-destination-documents-bucket
aws s3 rm --recursive s3://$base_name-parsers-$env-destination-ner-annotated-bucket
aws s3 rm --recursive s3://$base_name-parsers-$env-destination-squad-annotated-bucket
aws s3 rm --recursive s3://$base_name-parsers-$env-source-documents-bucket
aws s3 rm --recursive s3://$base_name-parsers-$env-source-ner-annotated-bucket
aws s3 rm --recursive s3://$base_name-parsers-$env-source-squad-annotated-bucket

aws cloudformation delete-stack --stack-name $base_name-publishers-$env
aws cloudformation wait stack-delete-complete --stack-name $base_name-publishers-$env
aws cloudformation delete-stack --stack-name $base_name-converters-$env
aws cloudformation wait stack-delete-complete --stack-name $base_name-converters-$env
aws cloudformation delete-stack --stack-name $base_name-parsers-$env
aws cloudformation wait stack-delete-complete --stack-name $base_name-parsers-$env
aws cloudformation delete-stack --stack-name $base_name-db-$env
aws cloudformation wait stack-delete-complete --stack-name $base_name-db-$env
aws cloudformation delete-stack --stack-name $base_name-lambda-packages-$env
aws cloudformation wait stack-delete-complete --stack-name $base_name-lambda-packages-$env