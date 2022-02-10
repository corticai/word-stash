""" Payload parsing - File containing functionality that parses documents into JSON payload representations.

Textual documents are ingested, and chunked json payload representations of the documents are created during this stage. The system is compatible with the following file formats:
- CSV files
- Word documents (docx)
- Emails (eml) and attachments that fall in the allowed file formats
- PDFs
- Text files (txt)
- Excel spreadsheets (excel)

    Typical usage example:
        import json
        import pytest
        from parsers import CsvToDictParser
        with open("tests/data/csv.json") as fp:
        example_dict = json.load(fp)
        fpath = 'tests/data/example.csv'
        parser = CsvToDictParser(word_count_limit=128)
        out_dict = parser.parse_file(fpath)
        print(str(out_dict))
"""

import abc
import base64
from pathlib import WindowsPath
import unicodedata
import re
import json
import html
import mailparser
import pandas as pd
from uuid import uuid4
from numpy.core.numeric import outer
from io import BytesIO
from pdfminer.layout import LTPage
from pdfminer.high_level import extract_pages
from typing import Any, List, Dict, Union
from datetime import datetime
from docx2python import docx2python
from docx2python.docx_output import TablesList
from mailparser import MailParser

ML_FILE_DATETIME = "%Y%m%d_%H%M%S"
UNICODE_FORM = "NFKD"
FILENAME_KEY = "filename"
FILETYPE_KEY = "filetype"
ID_KEY = "id"
INDEX_KEY = "index"
CONTENT_KEY = "content"
DATA_KEY = "data"
TIMESTAMP_KEY = "timestamp"

def create_iso_utc_timestamp() -> str:
    """function that generates a current timestamp in the ISO format
    Returns:
        str: A string timestamp in a ISO format
    """
    my_date = datetime.utcnow()
    return my_date.isoformat()

def create_file_datetime() -> str:
    """function that generates a file date time
    Returns:
        str: String in a yyyymmdd_hhmmss format
    """
    return str(uuid4()) + "-" + datetime.now().strftime(ML_FILE_DATETIME)

def split_str_by_word_count(input_str:str, word_count_limit:int=256, delimiter:chr=" ") -> List[str]:
    """Function that splits a string based on word count limit

    Args:
        input_str: Input string of string type
        word_count_limit: Word count limit of integer type
        delimiter: character that splits the string into words        

    Returns:
        A list (string type) of words

    Raises:
    """
    str_list = []
    if not input_str:
        return str_list
    str_list = input_str.split(delimiter)
    str_list = [' '.join(str_list[i: i + word_count_limit]) for i in range(0, len(str_list), word_count_limit)]
    return str_list

class AbstractParser(object):
    """AbstractParser"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def _parse(self, input_obj:Any, word_count_limit:int, meta_dict:dict) -> Dict:
        return

    @abc.abstractmethod
    def parse_bytes(self, input_bytes:bytes) -> Dict:
        return

    @abc.abstractmethod
    def parse_file(self, filename:str) -> Dict:
        return

class CsvToDictParser(AbstractParser):
    """CSV to Crude dictionary parser.

    Attributes:
        word_count_limit: An integer type word count limit per dictionary payload. This attribute is related to the chunking of text (https://en.wikipedia.org/wiki/Chunking_(writing))
        meta_dict: An optional dictionry containing addtional key value data that will be added to the dictionary.
    """
    def __init__(self, word_count_limit:int=256, meta_dict:dict={}):
        """__init__"""
        self.word_count_limit = word_count_limit
        self.meta_dict = meta_dict
        self.output_obj = { DATA_KEY: [] }

    def _parse_sheet(self, df:pd.DataFrame) -> str:
        """Converts a Pandas dataframe into a CSV comma delimited string.

        Args:
        df: Input pandas data frame

        Returns:
        string

        Raises:
        """
        df = df.to_string(index=False).split('\n')
        df = [', '.join(ele.split()) for ele in df]
        df = [element.replace('_',' ') for element in df]
        df = '\n'.join(df)
        return df

    def _parse(self, input_obj:pd.DataFrame, word_count_limit:int=256, meta_dict:dict={}) -> Dict:
        """Converts a Pandas dataframe into a Crude dictionary payload.

        Args:
        input_obj: Input pandas data frame
        word_count_limit: An integer type word count limit per dictionary payload. This attribute is related to the chunking of text (https://en.wikipedia.org/wiki/Chunking_(writing))
        meta_dict: An optional dictionry containing addtional key value data that will be added to the dictionary.

        Returns:
        dict

        Raises:
        """
        output_obj = { DATA_KEY: []}
        sheet_obj = self._parse_sheet(input_obj)

        str_list = split_str_by_word_count(sheet_obj, word_count_limit=word_count_limit)
        id = create_file_datetime()
        timestamp = create_iso_utc_timestamp()
        index = 0
        for str_element in str_list:
            element_dict = dict()
            element_dict.update(meta_dict)
            element_dict[TIMESTAMP_KEY] = timestamp
            element_dict[FILETYPE_KEY]  = "csv"
            element_dict[INDEX_KEY] = index
            element_dict[ID_KEY] = id
            element_dict[CONTENT_KEY] = str_element
            output_obj.get(DATA_KEY, []).append(element_dict)
            index += 1
        return output_obj

    def parse_bytes(self, input_bytes:bytes) -> Dict:
        """Converts bytes into a Crude dictionary payload.

        Args:
        input_bytes: Input bytes
        
        Returns:
        dict

        Raises:
        """
        bytes_io = BytesIO(input_bytes)
        input_obj = pd.read_csv(bytes_io)
        self.output_obj = self._parse(input_obj=input_obj, word_count_limit=self.word_count_limit, meta_dict=self.meta_dict)
        return self.output_obj

    def parse_file(self, filename:str) -> Dict:
        """Converts a file into a Crude dictionary payload.

        Args:
        filename: Filename of string type
        
        Returns:
        dict

        Raises:
        """
        input_obj = pd.read_csv(filename)
        self.output_obj = self._parse(input_obj=input_obj, word_count_limit=self.word_count_limit, meta_dict=self.meta_dict)
        return self.output_obj

class DocxToDictParser(AbstractParser):
    """Word document (docx) to Crude dictionary parser.

    Attributes:
        word_count_limit: An integer type word count limit per dictionary payload. This attribute is related to the chunking of text (https://en.wikipedia.org/wiki/Chunking_(writing))
        meta_dict: An optional dictionry containing addtional key value data that will be added to the dictionary.
    """
    def __init__(self, word_count_limit:int=256, meta_dict:dict={}):
        """__init__"""
        self.word_count_limit = word_count_limit
        self.meta_dict = meta_dict
        self.output_obj = { DATA_KEY: [] }

    def _is_table(self, input_obj:List) -> bool:
        """Method that validates if a list contains docx tables.

        Args:
        input_obj: list object
        
        Returns:
        boolean

        Raises:
        """
        if len(input_obj) > 1:
            return all(isinstance(n, list) for n in input_obj)
        return False

    def _parse_paragraph(self, input_obj:List) -> str:
        """Method that parses paragraphs into a string.

        Args:
        input_obj: list object
        
        Returns:
        string

        Raises:
        """
        output_obj = ""
        for doc_element in input_obj:
            output_obj += "\n".join([j for i in doc_element for j in i])
        return output_obj

    def _parse_table(self, input_obj:List) -> str:
        """Method that parses docx tables into a string.

        Args:
        input_obj: list object
        
        Returns:
        string

        Raises:
        """
        output_obj = ""
        for doc_element in input_obj:
            output_obj += '|'.join([k for j in doc_element for k in j]) + "\n"
        return output_obj

    def _parse(self, input_obj:TablesList, word_count_limit:int=256, meta_dict:dict={}) -> Dict:
        """Method that parses a docx2python TablesList into a Crude dictionary payload.

        Args:
        input_obj: TablesList object
        word_count_limit: An integer type word count limit per dictionary payload. This attribute is related to the chunking of text (https://en.wikipedia.org/wiki/Chunking_(writing))
        meta_dict: An optional dictionry containing addtional key value data that will be added to the dictionary.

        Returns:
        dict

        Raises:
        """
        output_obj = { DATA_KEY: []}
        id = create_file_datetime()
        timestamp = create_iso_utc_timestamp()
        index = 0
        for docx_element in input_obj.document:
            content = None
            if self._is_table(docx_element):
                content = self._parse_table(docx_element)
            else:
                content = self._parse_paragraph(docx_element)
            str_list = split_str_by_word_count(content, word_count_limit=word_count_limit)
            for str_element in str_list:
                element_dict = dict()
                element_dict.update(meta_dict)   
                element_dict[TIMESTAMP_KEY] = timestamp
                element_dict[FILETYPE_KEY] = "docx"
                element_dict.update(input_obj.core_properties)
                element_dict[INDEX_KEY] = index
                element_dict[ID_KEY] = id
                element_dict[CONTENT_KEY] = str_element
                output_obj.get(DATA_KEY, []).append(element_dict)
                index += 1
        return output_obj

    def parse_bytes(self, input_bytes:bytes) -> Dict:
        """Converts bytes into a Crude dictionary payload.

        Args:
        input_bytes: Input bytes
        
        Returns:
        dict

        Raises:
        """
        bytes_io = BytesIO(input_bytes)
        input_obj = docx2python(bytes_io)
        self.output_obj = self._parse(input_obj=input_obj, word_count_limit=self.word_count_limit, meta_dict=self.meta_dict)
        return self.output_obj

    def parse_file(self, filename:str) -> Dict:
        """Converts a file into a Crude dictionary payload.

        Args:
        filename: Filename of string type
        
        Returns:
        dict

        Raises:
        """
        input_obj = docx2python(filename)
        self.output_obj = self._parse(input_obj=input_obj, word_count_limit=self.word_count_limit, meta_dict=self.meta_dict)
        return self.output_obj

class EmailToDictParser(AbstractParser):
    """Email to Crude dictionary parser.

    Attributes:
        word_count_limit: An integer type word count limit per dictionary payload. This attribute is related to the chunking of text (https://en.wikipedia.org/wiki/Chunking_(writing))
        meta_dict: An optional dictionry containing addtional key value data that will be added to the dictionary.
    """
    def __init__(self, word_count_limit:int=256, meta_dict:dict={}):
        """__init__"""
        self.word_count_limit = word_count_limit
        self.meta_dict = meta_dict
        self.output_obj = { DATA_KEY: [] }

    def _remove_html(self, input_obj:str):
        """Method that removes html from a string

        Args:
        input_obj: Input object of string type data frame

        Returns:
        string

        Raises:
        """
        out_str = html.unescape(input_obj)
        out_str = unicodedata.normalize(UNICODE_FORM, re.sub('<[^<]+>', "", out_str))
        return out_str

    def _parse_attachment(self, input_obj:List[Dict], word_count_limit:int=256, meta_dict:dict={}) -> List:
        """method that parses an email's attachment into a Crude dictionary.

        Args:
        input_obj: input list with dict objects
        word_count_limit: An integer type word count limit per dictionary payload. This attribute is related to the chunking of text (https://en.wikipedia.org/wiki/Chunking_(writing))
        meta_dict: An optional dictionry containing addtional key value data that will be added to the dictionary.

        Returns:
        list

        Raises:
        """
        output_obj = list()
        parser_class_map = {
            "eml": EmailToDictParser,
            "txt": TxtToDictParser,
            "docx": DocxToDictParser,
            "csv": CsvToDictParser,
            "xlsx": XlsxToDictParser,
            "pdf": PdfToDictParser
        }
        timestamp = create_iso_utc_timestamp()
        for attachment in input_obj:
            binary = attachment["binary"]
            payload = attachment["payload"]
            filename = attachment["filename"]
            mail_content_type = attachment["mail_content_type"]
            file_ext = filename.split('.')[-1]
            parser_class = parser_class_map.get(file_ext, None)
            if not parser_class:
                continue
            parser = parser_class(word_count_limit=word_count_limit, meta_dict=meta_dict)
            if binary:
                payload = base64.b64decode(payload)
            attachment_dict = parser.parse_bytes(payload)
            attachment_dict.update(meta_dict)
            attachment_dict[TIMESTAMP_KEY] = timestamp
            attachment_dict[FILENAME_KEY] = filename
            attachment_dict[FILETYPE_KEY] = file_ext
            attachment_dict["mail_content_type"] = mail_content_type
            attachment_dict[CONTENT_KEY] = attachment_dict.pop(DATA_KEY)
            output_obj.append(attachment_dict)
        return output_obj

    def _parse(self, input_obj:MailParser, word_count_limit:int=256, meta_dict:dict={}) -> Dict:
        """Converts a MailParser object into a Crude dictionary payload.

        Args:
        input_obj: Input MailParser object
        word_count_limit: An integer type word count limit per dictionary payload. This attribute is related to the chunking of text (https://en.wikipedia.org/wiki/Chunking_(writing))
        meta_dict: An optional dictionry containing addtional key value data that will be added to the dictionary.

        Returns:
        dict

        Raises:
        """
        output_obj = { DATA_KEY: []}
        mail_dict = json.loads(input_obj.mail_json)
        body = self._remove_html(mail_dict.get("body", ""))
        str_list = split_str_by_word_count(body, word_count_limit=word_count_limit)
        id = create_file_datetime()
        timestamp = create_iso_utc_timestamp()
        index = 0
        for str_element in str_list:
            element_dict = dict()
            element_dict.update(meta_dict)
            element_dict[TIMESTAMP_KEY] = timestamp
            element_dict[FILETYPE_KEY]  = "eml"
            element_dict[INDEX_KEY] = index
            element_dict[ID_KEY] = id
            str_element = str_element.replace('\r', '')
            element_dict[CONTENT_KEY] = str_element
            output_obj.get(DATA_KEY, []).append(element_dict)
            index += 1
        if "attachments" in mail_dict.keys():
            if isinstance(mail_dict["attachments"], list):
                element_dict = dict()
                element_dict.update(meta_dict)
                element_dict[TIMESTAMP_KEY] = timestamp
                element_dict[FILETYPE_KEY]  = "attachments"
                element_dict[INDEX_KEY] = index
                element_dict[ID_KEY] = id
                element_dict[CONTENT_KEY] = self._parse_attachment(mail_dict["attachments"], word_count_limit=word_count_limit)
                output_obj.get(DATA_KEY, []).append(element_dict)
        return output_obj
            
    def parse_bytes(self, input_bytes:bytes) -> Dict:
        """Converts bytes into a Crude dictionary payload.

        Args:
        input_bytes: Input bytes
        
        Returns:
        dict

        Raises:
        """
        input_obj = mailparser.parse_from_bytes(input_bytes)
        self.output_obj = self._parse(input_obj, word_count_limit=self.word_count_limit, meta_dict=self.meta_dict)
        return self.output_obj

    def parse_file(self, filename:str) -> Dict:
        """Converts a file into a Crude dictionary payload.

        Args:
        filename: Filename of string type
        
        Returns:
        dict

        Raises:
        """
        input_obj = mailparser.parse_from_file(filename)
        self.output_obj = self._parse(input_obj, word_count_limit=self.word_count_limit, meta_dict=self.meta_dict)
        return self.output_obj

class PdfToDictParser(AbstractParser):
    """PDF to Crude dictionary parser.

    Attributes:
        word_count_limit: An integer type word count limit per dictionary payload. This attribute is related to the chunking of text (https://en.wikipedia.org/wiki/Chunking_(writing))
        meta_dict: An optional dictionry containing addtional key value data that will be added to the dictionary.
    """
    def __init__(self, word_count_limit:int=256, meta_dict:dict={}):
        """__init__"""
        self.word_count_limit = word_count_limit
        self.meta_dict = meta_dict
        self.output_obj = { DATA_KEY: [] }

    def _get_page_text(self, page_layout:LTPage) -> str:
        """Method that obtains the page number from an LTPage object.

        Args:
        page_layout: LTPage object

        Returns:
        string

        Raises:
        """
        page_text = ""
        for element in page_layout:
            if hasattr(element, "get_text"):
                page_text += element.get_text() + " "
        return page_text

    def _parse(self, input_obj:LTPage, word_count_limit:int=256, meta_dict:dict={}) -> Dict:
        """Converts an LTPage object into a Crude dictionary payload.

        Args:
        input_obj: Input LTPage object
        word_count_limit: An integer type word count limit per dictionary payload. This attribute is related to the chunking of text (https://en.wikipedia.org/wiki/Chunking_(writing))
        meta_dict: An optional dictionry containing addtional key value data that will be added to the dictionary.

        Returns:
        dict

        Raises:
        """
        output_obj = { DATA_KEY: []}
        id = create_file_datetime()
        timestamp = create_iso_utc_timestamp()
        index = 0
        for page_layout in input_obj:
            element_dict = dict()
            page_text = self._get_page_text(page_layout)
            str_list = split_str_by_word_count(page_text, word_count_limit=word_count_limit)
            for str_element in str_list:
                element_dict = dict()
                element_dict.update(meta_dict)
                element_dict[TIMESTAMP_KEY] = timestamp
                element_dict[FILETYPE_KEY] = "pdf"
                element_dict[INDEX_KEY] = index
                element_dict[ID_KEY] = id
                element_dict["page_id"] = page_layout.pageid
                element_dict[CONTENT_KEY] = str_element
                output_obj.get(DATA_KEY, []).append(element_dict)
                index += 1
        return output_obj 

    def parse_bytes(self, input_bytes:bytes) -> Dict:
        """Converts bytes into a Crude dictionary payload.

        Args:
        input_bytes: Input bytes
        
        Returns:
        dict

        Raises:
        """
        bytes_io = BytesIO(input_bytes)
        input_obj = extract_pages(bytes_io)
        self.output_obj = self._parse(input_obj=input_obj, word_count_limit=self.word_count_limit, meta_dict=self.meta_dict)
        return self.output_obj        

    def parse_file(self, filename:str) -> Dict:
        """Converts a file into a Crude dictionary payload.

        Args:
        filename: Filename of string type
        
        Returns:
        dict

        Raises:
        """
        input_obj = extract_pages(filename)
        self.output_obj = self._parse(input_obj=input_obj, word_count_limit=self.word_count_limit, meta_dict=self.meta_dict)
        return self.output_obj

class TxtToDictParser(AbstractParser):
    """Text file to Crude dictionary parser.

    Attributes:
        word_count_limit: An integer type word count limit per dictionary payload. This attribute is related to the chunking of text (https://en.wikipedia.org/wiki/Chunking_(writing))
        meta_dict: An optional dictionry containing addtional key value data that will be added to the dictionary.
    """
    def __init__(self, word_count_limit:int=256, meta_dict:dict={}):
        """__init__"""
        self.word_count_limit = word_count_limit
        self.meta_dict = meta_dict
        self.output_obj = { DATA_KEY: [] }

    def _parse(self, input_obj:str, word_count_limit:int=256, meta_dict:dict={}) -> Dict:
        """Converts an input string into a Crude dictionary payload.

        Args:
        input_obj: Input string
        word_count_limit: An integer type word count limit per dictionary payload. This attribute is related to the chunking of text (https://en.wikipedia.org/wiki/Chunking_(writing))
        meta_dict: An optional dictionry containing addtional key value data that will be added to the dictionary.

        Returns:
        dict

        Raises:
        """
        output_obj = { DATA_KEY: []}
        str_list = split_str_by_word_count(input_obj, word_count_limit=word_count_limit)
        id = create_file_datetime()
        timestamp = create_iso_utc_timestamp()
        index = 0
        for str_element in str_list:
            element_dict = dict()
            element_dict.update(meta_dict)
            element_dict[TIMESTAMP_KEY] = timestamp
            element_dict[FILETYPE_KEY]  = "txt"
            element_dict[INDEX_KEY] = index
            element_dict[ID_KEY] = id
            element_dict[CONTENT_KEY] = str_element
            output_obj.get(DATA_KEY, []).append(element_dict)
            index += 1
        return output_obj

    def parse_bytes(self, input_bytes:bytes) -> Dict:
        """Converts bytes into a Crude dictionary payload.

        Args:
        input_bytes: Input bytes
        
        Returns:
        dict

        Raises:
        """
        input_obj = input_bytes.decode("utf-8")
        self.output_obj = self._parse(input_obj=input_obj, word_count_limit=self.word_count_limit, meta_dict=self.meta_dict)
        return self.output_obj

    def parse_file(self, filename:str) -> Dict:
        """Converts a file into a Crude dictionary payload.

        Args:
        filename: Filename of string type
        
        Returns:
        dict

        Raises:
        """
        with open(filename, "r") as fp:
            input_obj = fp.read()
            self.output_obj = self._parse(input_obj=input_obj, word_count_limit=self.word_count_limit, meta_dict=self.meta_dict)
        return self.output_obj

class XlsxToDictParser(AbstractParser):
    """Excel to Crude dictionary parser.

    Attributes:
        word_count_limit: An integer type word count limit per dictionary payload. This attribute is related to the chunking of text (https://en.wikipedia.org/wiki/Chunking_(writing))
        meta_dict: An optional dictionry containing addtional key value data that will be added to the dictionary.
    """
    def __init__(self, word_count_limit:int=256, meta_dict:dict={}):
        """__init__"""
        self.word_count_limit = word_count_limit
        self.meta_dict = meta_dict
        self.output_obj = { DATA_KEY: [] }

    def _get_sheets(self, input_obj:str) -> List[str]:
        """Get Excel sheet names from a Excel string representation.

        Args:
        input_obj: Input string

        Returns:
        list

        Raises:
        """
        sheets = list()
        excel_file = pd.ExcelFile(input_obj)
        if excel_file:
            return excel_file.sheet_names
        return sheets

    def _parse_sheet(self, df:pd.DataFrame) -> str:
        """Converts a Pandas dataframe into an Excel comma delimited string.

        Args:
        df: Input pandas data frame

        Returns:
        string

        Raises:
        """
        df = df.to_string(index=False).split('\n')
        df = [', '.join(ele.split()) for ele in df]
        df = [element.replace('_',' ') for element in df]
        df = '\n'.join(df)
        return df

    def _parse(self, input_obj:Union[str, bytes], word_count_limit:int=256, meta_dict:dict={}) -> Dict:
        """Converts an Excel string representation into a Crude dictionary payload.

        Args:
        input_obj: Input pandas data frame
        word_count_limit: An integer type word count limit per dictionary payload. This attribute is related to the chunking of text (https://en.wikipedia.org/wiki/Chunking_(writing))
        meta_dict: An optional dictionry containing addtional key value data that will be added to the dictionary.

        Returns:
        dict

        Raises:
        """
        output_obj = { DATA_KEY: []}
        sheets = self._get_sheets(input_obj)

        id = create_file_datetime()
        timestamp = create_iso_utc_timestamp()
        index = 0

        for sheet_name in sheets:
            df = pd.read_excel(input_obj, sheet_name=sheet_name)
            sheet_obj = self._parse_sheet(df)
            str_list = split_str_by_word_count(sheet_obj, word_count_limit=word_count_limit)
            for str_element in str_list:
                element_dict = dict()
                element_dict.update(meta_dict)
                element_dict[TIMESTAMP_KEY] = timestamp
                element_dict[FILETYPE_KEY]  = "xlsx"
                element_dict[INDEX_KEY] = index
                element_dict[ID_KEY] = id
                element_dict["sheet_name"] = sheet_name
                element_dict[CONTENT_KEY] = str_element
                output_obj.get(DATA_KEY, []).append(element_dict)
                index += 1
        return output_obj

    def parse_bytes(self, input_bytes:bytes) -> Dict:
        """Converts bytes into a Crude dictionary payload.

        Args:
        input_bytes: Input bytes
        
        Returns:
        dict

        Raises:
        """
        bytes_io = BytesIO(input_bytes)
        self.output_obj = self._parse(input_obj=bytes_io, word_count_limit=self.word_count_limit, meta_dict=self.meta_dict)
        return self.output_obj

    def parse_file(self, filename:str) -> Dict:
        """Converts a file into a Crude dictionary payload.

        Args:
        filename: Filename of string type
        
        Returns:
        dict

        Raises:
        """
        self.output_obj = self._parse(input_obj=filename, word_count_limit=self.word_count_limit, meta_dict=self.meta_dict)
        return self.output_obj

class SQuADAnnotatedJsonToDictParser(AbstractParser):
    """Annotated SQuAD (https://rajpurkar.github.io/SQuAD-explorer/) to Crude dictionary parser.

    Attributes:
        word_count_limit: An integer type word count limit per dictionary payload. This attribute is related to the chunking of text (https://en.wikipedia.org/wiki/Chunking_(writing))
        meta_dict: An optional dictionry containing addtional key value data that will be added to the dictionary.
    """
    def __init__(self, word_count_limit:int=256, meta_dict:dict={}):
        """__init__"""
        self.word_count_limit = word_count_limit
        self.meta_dict = meta_dict
        self.output_obj = { DATA_KEY: [] }

    def _parse(self, input_obj:dict, word_count_limit:int=256, meta_dict:dict={}) -> Dict:
        """Method that parses a SQuAD dictionary into a Crude dictionary payload.

        Args:
        input_obj: dictionary object
        word_count_limit: An integer type word count limit per dictionary payload. This attribute is related to the chunking of text (https://en.wikipedia.org/wiki/Chunking_(writing))
        meta_dict: An optional dictionry containing addtional key value data that will be added to the dictionary.

        Returns:
        dict

        Raises:
        """
        output_obj = { DATA_KEY: []}
        id = create_file_datetime()
        timestamp = create_iso_utc_timestamp()
        index = 0
        for element_dict in input_obj.get(DATA_KEY, []):
            title = element_dict.get("title", None)
            for paragraph in element_dict.get("paragraphs", []):
                out_dict = dict(paragraph)
                out_dict["title"] = title
                out_dict[FILETYPE_KEY]  = "squad_annotated"
                out_dict[INDEX_KEY] = index
                out_dict[ID_KEY] = id
                out_dict.update(meta_dict)
                out_dict[TIMESTAMP_KEY] = timestamp
                output_obj.get(DATA_KEY, []).append(out_dict)
                index += 1
        return output_obj

    def parse_bytes(self, input_bytes:bytes) -> Dict:
        """Converts bytes into a Crude dictionary payload.

        Args:
        input_bytes: Input bytes
        
        Returns:
        dict

        Raises:
        """
        input_obj = json.loads(input_bytes)
        self.output_obj = self._parse(input_obj=input_obj, word_count_limit=self.word_count_limit, meta_dict=self.meta_dict)
        return self.output_obj

    def parse_file(self, filename:str) -> Dict:
        """Converts a file into a Crude dictionary payload.

        Args:
        filename: Filename of string type
        
        Returns:
        dict

        Raises:
        """
        with open(filename, "r") as fp:
            input_obj = json.load(fp)
            self.output_obj = self._parse(input_obj=input_obj, word_count_limit=self.word_count_limit, meta_dict=self.meta_dict)
        return self.output_obj

class NERAnnotatedJsonlToDictParser(AbstractParser):
    """Annotated BILUO Named Entity Recognition ((https://towardsdatascience.com/extend-named-entity-recogniser-ner-to-label-new-entities-with-spacy-339ee5979044)) to Crude dictionary parser.

    Attributes:
        word_count_limit: An integer type word count limit per dictionary payload. This attribute is related to the chunking of text (https://en.wikipedia.org/wiki/Chunking_(writing))
        meta_dict: An optional dictionry containing addtional key value data that will be added to the dictionary.
    """
    def __init__(self, word_count_limit:int=256, meta_dict:dict={}):
        """__init__"""
        self.word_count_limit = word_count_limit
        self.meta_dict = meta_dict
        self.output_obj = { DATA_KEY: [] }

    def _parse(self, input_obj:str, word_count_limit:int=256, meta_dict:dict={}) -> Dict:
        """Method that parses a NER BILUO dictionary into a Crude dictionary payload.

        Args:
        input_obj: dictionary object
        word_count_limit: An integer type word count limit per dictionary payload. This attribute is related to the chunking of text (https://en.wikipedia.org/wiki/Chunking_(writing))
        meta_dict: An optional dictionry containing addtional key value data that will be added to the dictionary.

        Returns:
        dict

        Raises:
        """
        input_obj = [json.loads(jline) for jline in input_obj.splitlines()]
        output_obj = { DATA_KEY: []}
        id = create_file_datetime()
        timestamp = create_iso_utc_timestamp()
        index = 0
        for elem in input_obj:
            element_dict = dict(elem)
            element_dict.update(meta_dict)
            element_dict[TIMESTAMP_KEY] = timestamp
            element_dict[FILETYPE_KEY]  = "ner_annotated"
            element_dict[INDEX_KEY] = index
            element_dict[ID_KEY] = id
            output_obj.get(DATA_KEY, []).append(element_dict)
            index += 1
        return output_obj

    def parse_bytes(self, input_bytes:bytes) -> Dict:
        """Converts bytes into a Crude dictionary payload.

        Args:
        input_bytes: Input bytes
        
        Returns:
        dict

        Raises:
        """
        input_obj = input_bytes.decode("utf-8")
        self.output_obj = self._parse(input_obj=input_obj, word_count_limit=self.word_count_limit, meta_dict=self.meta_dict)
        return self.output_obj

    def parse_file(self, filename:str) -> Dict:
        """Converts a file into a Crude dictionary payload.

        Args:
        filename: Filename of string type
        
        Returns:
        dict

        Raises:
        """
        with open(filename, "r") as fp:
            input_obj = fp.read()
            self.output_obj = self._parse(input_obj=input_obj, word_count_limit=self.word_count_limit, meta_dict=self.meta_dict)
        return self.output_obj