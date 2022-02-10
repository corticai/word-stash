""" Publisher functions
"""
from uuid import uuid4
from datetime import datetime

ML_FILE_DATETIME = "%Y%m%d_%H%M%S"

def create_file_datetime() -> str:
    """function that generates a file date time
    Returns:
        str: String in a yyyymmdd_hhmmss format
    """
    return str(uuid4()) + "-" + datetime.now().strftime(ML_FILE_DATETIME)