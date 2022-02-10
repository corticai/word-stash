""" S3 event trigger compatible Lambda function that transforms a Word document docx file into a Crude json file and writes it to S3.
"""
from typing import Any, Dict
import os
import sys
import urllib.parse
from s3_functions import read_s3_bytes, write_dict_to_s3
from parsers import create_file_datetime, DocxToDictParser
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_extension = "docx"

def lambda_handler(event: Dict[str, Any], context):
    """S3 event trigger compatible Lambda function handler that transforms a Word document docx into a Crude json file and writes it to S3.

    Args:
        event: S3 event trigger (dict)
        context: Lambda context contains methods and properties that provide information about the invocation, function, and execution environment (dict)
    Returns:
        list (File S3 upload response dict)
    Raises:
    """
    destination_bucket = os.getenv("DESTINATION_BUCKET", None)
    word_count_limit = int(os.getenv("WORD_COUNT_LIMIT", 256))
    write_data_json_array_in_chunks_flag = os.getenv("WRITE_DATA_JSON_ARRAY_IN_CHUNKS_FLAG", "false").lower() in ("yes", "true", "t", "1")
    date_time = create_file_datetime()
    resp = list()
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        try:
            if not key.endswith("." + file_extension):
                logger.warning("file must be [file_name]."+ file_extension +". Ignoring file: " + str(key))
                continue
            key = urllib.parse.unquote_plus(key)
            input_bytes = read_s3_bytes(bucket=bucket, key=key)
            parser = DocxToDictParser(word_count_limit=word_count_limit, meta_dict={"filename": os.path.join("s3://" + bucket, key), "filetype": file_extension})
            out_dict = parser.parse_bytes(input_bytes=input_bytes)
            if not write_data_json_array_in_chunks_flag:
                out_key = "-".join(key.split(".")) + "-" + date_time + ".json"
                resp.append(write_dict_to_s3(bucket=destination_bucket, key=out_key, input_dict=out_dict))
            else:
                for i, data_dict in enumerate(out_dict["data"]):
                    index_str = "{:010d}".format(i)
                    out_key = "-".join(key.split(".")) + "-" + date_time + "-" + index_str + ".json"
                    resp.append(write_dict_to_s3(bucket=destination_bucket, key=out_key, input_dict=data_dict))
        except Exception:
            ex_type, ex_value, ex_traceback = sys.exc_info()
            logger.error("bucket: {bucket}, key: {key}, exception_type: {ex_type}, exception_value: {ex_value}, exception_traceback: {ex_traceback}".format(bucket=bucket, key=key, ex_type=ex_type, ex_value=ex_value, ex_traceback=ex_traceback))
    return resp