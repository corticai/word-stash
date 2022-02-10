""" Converter dictionary schema validator definitions
"""
FIREHOSE_SCHEMA = {
        "type": "object",
        "properties": {
            "records": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "recordId": {
                        "type": "string"
                    },
                    "data": {
                        "contentEncoding": "base64",
                        "contentMediaType": "text/plain"
                    },
                    "result": {
                        "type": "string"
                    }
                },
                "required": ["recordId", "data"]
            }
        }
    },
    "required": ["records"]
}

CLASS_CRUDE_SCHEMA = {
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
        },
        "label": {
            "type": ["string", "null"]
        }
    },
    "required": ["index", "id", "content"]
}

CLASS_LABEL_SCHEMA = {
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
        "sentence1": {
            "type": ["string", "null"]
        },
        "sentence2": {
            "type": ["string", "null"]
        },
        "label": {
            "type": ["string", "null"]
        }
    },
    "required": ["index", "id", "sentence1", "label"]
}

NER_CRUDE_SCHEMA = {
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

NER_TRAIN_SCHEMA = {
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
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "label": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "required": ["index", "id", "text", "label"]
}

SQUAD_CRUDE_SCHEMA = {
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
            "type": "string"
        },
        "label": {
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
    "required": ["index", "id", "content"]
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

SQUAD_TRAIN_SCHEMA = {
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
        "question": {
            "type": "string"
        },
        "answers": {
            "type": "object",
            "properties": {
                "answer_start": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    }
                },
                "text": {
                    "type": "array",
                    "items": {
                        "type": ["string", "null"]
                    }
                }
            }
        }
    },
    "required": ["index", "id", "context", "question", "answers"]
}