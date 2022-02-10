""" Eventbridge compatible Lambda function that published Named Entity Recognition (NER) payloads to the Kinesis Firehose delivery stream.
"""
from typing import Any, Dict
import os
import sys
import urllib.parse
import json
import boto3
from jsonschema import validate
from schema_validators import NER_LABEL_SCHEMA
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

json_extension = "json"
jsonl_extension = "jsonl"
valid_file_extensions = [json_extension, jsonl_extension]

def lambda_handler(event: Dict[str, Any], context):
    """Eventbridge compatible Lambda function that published Named Entity Recognition (NER) payloads stored in S3 to the Kinesis Firehose delivery stream.

    Args:
        event: Eventbridge message (dict)
        context: Lambda context contains methods and properties that provide information about the invocation, function, and execution environment (dict)
    Returns:
        list (Kinesis Firehose delivery stream response dict)
    Raises:
    """
    stream_name = os.getenv("STREAM_NAME", None)
    region = os.getenv("AWS_REGION", None)
    bucket = event['detail']['bucket']['name']
    key = event['detail']['object']['key']
    resp = list()
    logger.info("Processing s3 key: s3://" + os.path.join(str(bucket), str(key)))
    try:
        file_extension = key.split(".")[-1]
        if file_extension not in valid_file_extensions:
            raise ValueError("file must be [file_name]."+ file_extension +". Ignoring file: " + str(key))
        key = urllib.parse.unquote_plus(key)
        s3 = boto3.resource('s3')
        obj = s3.Object(bucket, key)
        output_json = obj.get()['Body'].read().decode("utf-8")
        kinesis_client = boto3.client('firehose', region)
        if file_extension == jsonl_extension:
            json_list = output_json.split('\n')
            records = list()
            for json_elem in json_list:
                try:
                    validate(json.loads(json_elem), NER_LABEL_SCHEMA)
                    records.append({"Data": json_elem})
                except Exception:
                    ex_type, ex_value, ex_traceback = sys.exc_info()
                    logger.error("bucket: {bucket}, key: {key}, json_elem: {json_elem}, exception_type: {ex_type}, exception_value: {ex_value}, exception_traceback: {ex_traceback}".format(bucket=bucket, key=key, json_elem=json_elem, ex_type=ex_type, ex_value=ex_value, ex_traceback=ex_traceback))
            resp.append(kinesis_client.put_record_batch(
                DeliveryStreamName=stream_name,
                Records=records))
        else:
            validate(json.loads(output_json), NER_LABEL_SCHEMA)
            resp.append(kinesis_client.put_record(
                DeliveryStreamName=stream_name,
                Record={"Data": output_json}))
    except Exception:
        ex_type, ex_value, ex_traceback = sys.exc_info()
        logger.error("bucket: {bucket}, key: {key}, output_json: {output_json}, exception_type: {ex_type}, exception_value: {ex_value}, exception_traceback: {ex_traceback}".format(bucket=bucket, key=key, output_json=output_json, ex_type=ex_type, ex_value=ex_value, ex_traceback=ex_traceback))
    return resp
