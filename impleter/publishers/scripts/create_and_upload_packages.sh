 #!/bin/bash

lambda_layer_name=impleter-publishers-lambda-packages
lambda_function_array=( crude-publisher class-crude-label-publisher ner-crude-label-publisher ner-label-train-publisher squad-crude-label-publisher squad-label-train-publisher )

s3_bucket=$LAMBDA_PACKAGES_S3_BUCKET
lambda_layer_s3_key=$IMPLETER_PUBLISHERS_LAMBDA_LAYER_ZIP_S3_KEY
lambda_s3_key=$IMPLETER_PUBLISHERS_SOURCE_ZIP_S3_KEY
mkdir -p packages/python
pip install -r requirements.txt --target packages/python
(cd packages; zip -r ../lambda_layer_package.zip .)
echo "Uploading lambda layer"
resp=`aws s3 cp lambda_layer_package.zip s3://$s3_bucket/$lambda_layer_s3_key`
echo "$resp"
(cd src; zip -r ../lambda_package.zip .)
echo "Uploading lambda source code"
resp=`aws s3 cp lambda_package.zip s3://$s3_bucket/$lambda_s3_key`
echo "$resp"
lambda_layer_arn=`aws lambda list-layers --query "Layers[?LayerName=='$lambda_layer_name'].LatestMatchingVersion.LayerVersionArn" --output text`

if [ -z "$lambda_layer_arn" ]; then 
    echo "Lambda layer $lambda_layer_arn does not exist. Continue"; 
else 
    echo "Lambda layer $lambda_layer_arn exists. Updating";
    resp=`aws lambda publish-layer-version --layer-name $lambda_layer_name --license-info "MIT" --content S3Bucket=$s3_bucket,S3Key=$lambda_layer_s3_key --compatible-runtimes python3.8`
    echo "$resp"
fi

lambda_layer_arn=`aws lambda list-layers --query "Layers[?LayerName=='$lambda_layer_name'].LatestMatchingVersion.LayerVersionArn" --output text`
echo "Lambda layer ARN: $lambda_layer_arn"

for lambda_fn_name in "${lambda_function_array[@]}"
do
    echo "Processing lambda function: $lambda_fn_name"
    lambda_fn=`aws lambda get-function --function-name $lambda_fn_name`
    if [ -z "$lambda_fn" ]; then 
        echo "Lambda function $lambda_fn_name does not exist. Continue"; 
    else 
        echo "Lambda function $lambda_fn_name exists. Updating";
        if [ ! -z "$lambda_fn" ]; then 
            echo "Updating lambda layer"
            resp=`aws lambda update-function-configuration --function-name $lambda_fn_name  --layers $lambda_layer_arn`
            echo "$resp"
        fi
        echo "Updating function code"
        resp=`aws lambda update-function-code --function-name  $lambda_fn_name --s3-bucket $s3_bucket --s3-key $lambda_s3_key`
        echo "Result - function code update: $resp"
    fi
done