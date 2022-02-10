""" Publisher dictionary schema validator definitions
"""
CRUDE_SCHEMA = {
    "type": "object",
    "properties": {
        "filename": {
            "type": ["string", "null"]
        },
        "filetype": {
            "type": ["string", "null"]
        },
        "index": {
            "type": "integer"
        },
        "id": {
            "type": "string"
        },
        "content": {
            "type": ["string", "null"]
        },
        "content2": {
            "type": ["string", "null"]
        }
    },
    "required": ["index", "id", "content"]
}

NER_LABEL_SCHEMA = {
    "type": "object",
    "properties": {
        "filename": {
            "type": ["string", "null"]
        },
        "filetype": {
            "type": ["string", "null"]
        },
        "index": {
            "type": "integer"
        },
        "id": {
            "type": "string"
        },
        "text": {
            "type": "string"
        },
        "label": {
            "type": "array",
            "items": {
                "type": "array",
                "prefixItems": [
                    {
                        "type": ["integer", "string"]
                    }, 
                    {
                        "type": ["integer", "string"]
                    },
                    {
                        "type": "string"
                    }
                ]
            }
        }
    },
    "required": ["index", "id", "text", "label"]
}


SQUAD_LABEL_SCHEMA = {
    "type": "object",
    "properties": {
        "filename": {
            "type": ["string", "null"]
        },
        "filetype": {
            "type": ["string", "null"]
        },
        "index": {
            "type": "integer"
        },
        "id": {
            "type": "string"
        },
        "context": {
            "type": "string"
        },
        "qas": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string"
                    },
                    "answers": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "answer_start": {
                                    "type": "integer"
                                },
                                "text": {
                                    "type": ["string", "null"]
                                }
                             }
                        }
                    }
                }
            }
        }
    },
    "required": ["index", "id", "context", "qas"]
}