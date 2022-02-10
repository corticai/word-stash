firehose_payload_schema = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "title": "Firehose payload schema",
    "description": "The required fields from the scorer",
    "required": ["invocationId", "deliveryStreamArn", "region", "records"],
    "properties": {
        "invocationId": {
            "$id": "#/properties/invocationId",
            "type": "string",
            "title": "Invocation ID"
        },
        "deliveryStreamArn": {
            "$id": "#/properties/deliveryStreamArn",
            "type": "string",
            "title": "Delivery Stream Arn",
        },
        "region": {
            "$id": "#/properties/region",
            "type": "string",
            "title": "AWS region",
        },
        "records": {
            "$id": "#/properties/region",
            "type": "array",
            "title": "Array of records",
        },
    }
}