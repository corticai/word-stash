import os
import sys
import base64
import json

sys.path.append(os.path.realpath(os.path.dirname(__file__) + "/../src"))
from src import (
    class_crude_to_label_lambda_function,
    ner_crude_to_label_lambda_function,
    ner_label_to_train_lambda_function,
    squad_crude_to_label_lambda_function,
    squad_label_to_train_lambda_function
)


class LambdaContextObject:
    def __init__(self):
        self.function_name= 'test-lambda'
        self.memory_limit_in_mb = 512
        self.invoked_function_arn = 'arn:arn'
        self.aws_request_id = '112312313'

def convert_base64_to_dict(event:dict):
    for record in event["records"]:
        payload = base64.b64decode(record['data'])
        payload = json.loads(payload)
        record['data'] = payload
    return event


def test_class_crude_to_label_returns_correct_value():
    data = base64.b64encode(json.dumps({
        "filename": "/Users/eugenetan/Downloads/EY/papers/pdf//CORTICAI-57639482-160721-1931.pdf",
        "section_0": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
        "section_1": "Principles of Established Science",
        "section_2": "",
        "id": "CORTICAI-57639482-160721-1931_1",
        "index": 12345,
        "content": "The field of machine learning has made tremendous progress over the past decade",
        "page": 1,
        "title": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
        "label": "scientific_context"
    }).encode('utf-8'))
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
    assert actual == {
        "records": [
            {
                "recordId": "49583354031560888214100043296632351296610463251381092354000000",
                "data": {
                    "filename": "/Users/eugenetan/Downloads/EY/papers/pdf//CORTICAI-57639482-160721-1931.pdf",
                    "section_0": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
                    "section_1": "Principles of Established Science",
                    "section_2": "",
                    "id": "CORTICAI-57639482-160721-1931_1",
                    "index": 12345,
                    "sentence1": "The field of machine learning has made tremendous progress over the past decade",
                    'sentence2': None,
                    "page": 1,
                    "title": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
                    "label": "scientific_context"
                },
                "result": "Ok"
            }
        ]
    }


def test_ner_crude_to_label_returns_correct_value():
    data = base64.b64encode(json.dumps({
        "filename": "/Users/eugenetan/Downloads/EY/papers/pdf//CORTICAI-57639482-160721-1931.pdf",
        "section_0": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
        "section_1": "Principles of Established Science",
        "section_2": "",
        "id": "CORTICAI-57639482-160721-1931_1",
        "index": 12345,
        "content": "The field of machine learning has made tremendous progress over the past decade",
        "page": 1,
        "title": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
        "label": [[4, 9, "U-LOC"]]
    }).encode('utf-8'))
    valid_input_event = {
        "records": [
            {
                "recordId": "49583354031560888214100043296632351296610463251381092354000000",
                "data": data
            }
        ]
    }
    context = LambdaContextObject()
    
    actual = ner_crude_to_label_lambda_function.lambda_handler(valid_input_event, context)
    actual = convert_base64_to_dict(actual)
    print("actual: " + str(actual))
    assert actual == {
        "records": [
            {
                "recordId": "49583354031560888214100043296632351296610463251381092354000000",
                "data": {
                    "filename": "/Users/eugenetan/Downloads/EY/papers/pdf//CORTICAI-57639482-160721-1931.pdf",
                    "section_0": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
                    "section_1": "Principles of Established Science",
                    "section_2": "",
                    "id": "CORTICAI-57639482-160721-1931_1",
                    "index": 12345,
                    "text": "The field of machine learning has made tremendous progress over the past decade",
                    "page": 1,
                    "title": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
                    "label": [["4", "9", "U-LOC"]]
                },
                "result": "Ok"
            }
        ]
    }


def test_ner_label_to_train_returns_correct_value():
    data = base64.b64encode(json.dumps({
        "filename": "/Users/eugenetan/Downloads/EY/papers/pdf//CORTICAI-57639482-160721-1931.pdf",
        "section_0": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
        "section_1": "Principles of Established Science",
        "section_2": "",
        "id": "CORTICAI-57639482-160721-1931_1",
        "index": 12345,
        "text": "The field of machine learning has made tremendous progress over the past decade",
        "page": 1,
        "title": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
        "label": [[4, 9, "U-LOC"]]
    }).encode('utf-8'))
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
    
    actual = ner_label_to_train_lambda_function.lambda_handler(valid_input_event, context)
    actual = convert_base64_to_dict(actual)
    assert actual == {
        'records': [{
            'recordId': '49583354031560888214100043296632351296610463251381092354000000',
            'result': 'Ok',
            'data': {
                'text': [
                    'The',
                    'field',
                    'of',
                    'machine',
                    'learning',
                    'has',
                    'made',
                    'tremendous',
                    'progress',
                    'over',
                    'the',
                    'past',
                    'decade'],
                    'label': ['O',
                    'U-LOC',
                    'O',
                    'O',
                    'O',
                    'O',
                    'O',
                    'O',
                    'O',
                    'O',
                    'O',
                    'O',
                    'O'],
                'filename': '/Users/eugenetan/Downloads/EY/papers/pdf//CORTICAI-57639482-160721-1931.pdf',
                'section_0': 'Machine Learning: Diagnosis of COVID-19 based on Lab Tests',
                'section_1': 'Principles of Established Science',
                'section_2': '',
                'id': 'CORTICAI-57639482-160721-1931_1',
                'index': 12345,
                'page': 1,
                'title': 'Machine Learning: Diagnosis of COVID-19 based on Lab Tests'
            }
        }]}


def test_squad_crude_to_label_returns_correct_value():
    data = base64.b64encode(json.dumps({
        "filename": "/Users/eugenetan/Downloads/EY/papers/pdf//CORTICAI-57639482-160721-1931.pdf",
        "section_0": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
        "section_1": "Principles of Established Science",
        "section_2": "",
        "id": "CORTICAI-57639482-160721-1931_1",
        "index": 12345,
        "content": "The field of machine learning has made tremendous progress over the past decade",
        "page": 1,
        "title": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
        "label": [{"question": "What has made progress?", "answers":[{"answer_start": 0, "text": "The field of machine learning has made tremendous progress over the past decade"}]}]
    }).encode('utf-8'))
    valid_input_event = {
        "records": [
            {
                "recordId": "49583354031560888214100043296632351296610463251381092354000000",
                "data": data
            }
        ]
    }
    context = LambdaContextObject()
    
    actual = squad_crude_to_label_lambda_function.lambda_handler(valid_input_event, context)
    actual = convert_base64_to_dict(actual)
    print("actual: " + str(actual))
    assert actual == {
        "records": [
            {
                "recordId": "49583354031560888214100043296632351296610463251381092354000000",
                "data": {
                    "id": "CORTICAI-57639482-160721-1931_1",
                    "index": 12345,
                    "filename": "/Users/eugenetan/Downloads/EY/papers/pdf//CORTICAI-57639482-160721-1931.pdf",
                    "section_0": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
                    "section_1": "Principles of Established Science",
                    "section_2": "",
                    "page": 1,
                    "title": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
                    "qas": [
                        {
                            "question": "What has made progress?",
                            "answers": [
                                {
                                    "answer_start": 0,
                                    "text": "The field of machine learning has made tremendous progress over the past decade"
                                }
                            ]
                        }],
                    "context": "The field of machine learning has made tremendous progress over the past decade"},
                "result": "Ok"
            }]
    }


def test_squad_label_to_train_returns_correct_value():
    data = base64.b64encode(json.dumps({
        "id": "CORTICAI-57639482-160721-1931_1",
        "index": 12345,
        "filename": "/Users/eugenetan/Downloads/EY/papers/pdf//CORTICAI-57639482-160721-1931.pdf",
        "section_0": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
        "section_1": "Principles of Established Science",
        "section_2": "",
        "page": 1,
        "title": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
        "context": "The field of machine learning has made tremendous progress over the past decade",
        "qas": [
            {
                "question": "What has made progress?",
                "answers": [{
                    "answer_start": 0,
                    "text": "The field of machine learning has made tremendous progress over the past decade"
                }]
            }]}).encode('utf-8'))
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
    
    actual = squad_label_to_train_lambda_function.lambda_handler(valid_input_event, context)
    actual = convert_base64_to_dict(actual)
    print("actual: " + str(actual))
    actual["records"][0]["data"]["data"][0]["id"] = "CORTICAI-57639482-160721-1931_1"
    assert actual == {
        "records": [
            {
                "recordId": "49583354031560888214100043296632351296610463251381092354000000",
                "data": {   
                        "data": [{
                            "id": "CORTICAI-57639482-160721-1931_1",
                            "index": 12345,
                            "filename": "/Users/eugenetan/Downloads/EY/papers/pdf//CORTICAI-57639482-160721-1931.pdf",
                            "section_0": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
                            "section_1": "Principles of Established Science",
                            "section_2": "",
                            "page": 1,
                            "title": "Machine Learning: Diagnosis of COVID-19 based on Lab Tests",
                            "context": "The field of machine learning has made tremendous progress over the past decade",
                            "question": "What has made progress?",
                            "answers": {
                                "answer_start": [0],
                                "text": ["The field of machine learning has made tremendous progress over the past decade"]
                            }
                        }]
                    },
                "result": "Ok"
            }
        ]
    }