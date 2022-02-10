import boto3
import json

def read_s3_bytes(bucket:str, key:str) -> bytes:
    output_bytes = None
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket, key)
    output_bytes = obj.get()['Body'].read()
    return output_bytes

def write_dict_to_s3(bucket:str, key:str, input_dict:dict) -> bytes:
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket, key)
    result = obj.put(Body=json.dumps(input_dict))
    return result
