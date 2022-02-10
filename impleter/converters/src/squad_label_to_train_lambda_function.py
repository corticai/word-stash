
""" Kinesis Firehose compatible Lambda function that converts a SQuAD question-answer annotator dictionary to Hugging Face Transformer question-answer dictionary converter


The Kinesis Firehose dictionary payload representations are transformed into the following machine learning formats:
-  Hugging Face Transformer question-answer - https://www.tensorflow.org/datasets/catalog/squad#:~:text=Stanford%20Question%20Answering%20Dataset%20(SQuAD,the%20question%20might%20be%20unanswerable.

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
            "id": "57639482-160721-1931_1",
            "index": 12345,
            "filename": "test.pdf",
            "title": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
            "context": "The field of machine learning has made tremendous progress over the past decade",
            "qas": [
                {
                    "question": "What has made progress?",
                    "answers": [{
                        "answer_start": 0,
                        "text": "The field of machine learning has made tremendous progress over the past decade"
                    }]
                }]}
        data = base64.b64encode(json.dumps(test_payload).encode('utf-8'))
        valid_input_event = {
            "records": [
                {
                    "recordId": "49583354031560888214100043296632351296610463251381092354000000",
                    "data": data,
                    "result": "Ok"
                }
            ]
        }
        context = LambdaContextObject()
        
        converted_payload = squad_label_to_train_lambda_function.lambda_handler(valid_input_event, context)
        converted_payload = convert_base64_to_dict(converted_payload)
        print("converted_payload: " + str(converted_payload))
"""
from typing import Any, Dict
from jsonschema import validate
from schema_validators import FIREHOSE_SCHEMA, SQUAD_TRAIN_SCHEMA, SQUAD_LABEL_SCHEMA
from converters import SquadLabelToTrain
import sys
import base64
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context):
    """Kinesis Firehose compatible Lambda function handler that converts a SQuAD question-answer annotator dictionary to Hugging Face Transformer question-answer dictionary converter

    Args:
        event: Kinesis Firehose event (dict)
        context: Lambda context contains methods and properties that provide information about the invocation, function, and execution environment (dict)
    Returns:
        dict (Kinesis Firehose compatible converted Hugging Face Transformer question-answer dictionary)
    Raises:
    """
    output = []
    converter = SquadLabelToTrain()
    validate(event, FIREHOSE_SCHEMA)
    for record in event["records"]:
        try:
            logger.info("recordId: " + record['recordId'])
            payload = base64.b64decode(record['data'])
            payload = json.loads(payload)
            validate(payload, SQUAD_LABEL_SCHEMA)
            converted_payload = converter.convert(payload)
            if isinstance(converted_payload['data'], list):
                [validate(i, SQUAD_TRAIN_SCHEMA) for i in converted_payload['data']]
            else:
                validate(converted_payload['data'], SQUAD_TRAIN_SCHEMA)
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