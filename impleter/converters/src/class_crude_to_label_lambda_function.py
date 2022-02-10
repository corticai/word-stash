""" Kinesis Firehose compatible Lambda function that converts crude/raw dictionary into a text classification dictionary 


The Kinesis Firehose dictionary payload representations are transformed into the following machine learning formats:
- Text classification (https://developers.google.com/machine-learning/guides/text-classification)

    Typical usage example:
        import os
        import sys
        import base64
        import json

        def convert_base64_to_dict(event:dict):
            for record in event["records"]:
                payload = base64.b64decode(record['data'])
                payload = json.loads(payload)
                record['data'] = payload
            return event
        test_payload = {
            "filename": "test.pdf",
            "section_0": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
            "id": "160721-1931_1",
            "index": 12345,
            "content": "The field of machine learning has made tremendous progress over the past decade",
            "page": 1,
            "title": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
            "label": "scientific_context"
        }
        data = base64.b64encode(json.dumps(test_payload).encode('utf-8'))
        valid_input_event = {
            "records": [
                {
                    "recordId": "49583354031560888214100043296632351296610463251381092354000000",
                    "data": data
                }
            ]
        }
        context = LambdaContextObject()
        
        actual = class_crude_to_label_lambda_function.lambda_handler(valid_input_event, context)
        actual = convert_base64_to_dict(actual)
        print(str(actual))
"""
from typing import Any, Dict
from jsonschema import validate
from schema_validators import FIREHOSE_SCHEMA, CLASS_CRUDE_SCHEMA, CLASS_LABEL_SCHEMA
from converters import ClassificationCrudeToLabel
import sys
import base64
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context):
    """Kinesis Firehose compatible Lambda function handler that converts crude/raw dictionary into a text classification dictionary 

    Args:
        event: Kinesis Firehose event (dict)
        context: Lambda context contains methods and properties that provide information about the invocation, function, and execution environment (dict)
    Returns:
        dict (Kinesis Firehose compatible converted text classification dictionary)

    Raises:
    """
    output = []
    converter = ClassificationCrudeToLabel()
    validate(event, FIREHOSE_SCHEMA)
    for record in event["records"]:
        try:
            logger.info("recordId: " + record['recordId'])
            payload = base64.b64decode(record['data'])
            payload = json.loads(payload)
            validate(payload, CLASS_CRUDE_SCHEMA)
            converted_payload = converter.convert(payload) 
            validate(converted_payload, CLASS_LABEL_SCHEMA)
            converted_payload = json.dumps(converted_payload)
            converted_payload = converted_payload.encode('utf-8')
            output_record = {
                'recordId': record['recordId'],
                'result': 'Ok',
                'data': base64.b64encode(converted_payload)
            }
            output.append(output_record)
        except Exception:
            ex_type, ex_value, ex_traceback = sys.exc_info()
            logger.error("recordId: {recordId}, exception_type: {ex_type}, exception_value: {ex_value}, exception_traceback: {ex_traceback}".format(recordId=record['recordId'], ex_type=ex_type, ex_value=ex_value, ex_traceback=ex_traceback))
            output_record = {
                'recordId': record['recordId'],
                'result': 'Nok',
                'data': record["data"],
                'exception_type': ex_type,
                'exception_value': ex_value,
                'exception_traceback': ex_traceback
            }
            output.append(output_record)
    return {'records': output}
