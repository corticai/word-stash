import json
import pytest
from src.parsers import (
    TxtToDictParser,
    CsvToDictParser,
    DocxToDictParser,
    EmailToDictParser,
    PdfToDictParser,
    XlsxToDictParser,
    SQuADAnnotatedJsonToDictParser,
    NERAnnotatedJsonlToDictParser
)

def delete_key_from_content(input_dict:dict, key:str) -> dict:
    for element in input_dict.get("data", []):
        if key in element.keys():
            del element[key]
        if "content" not in element.keys():
            continue
        content = element["content"]
        if not isinstance(content, list):
            continue
        for content_element in content:
            if key in content_element.keys():
                del content_element[key]
            if "content" in content_element.keys():
                if not isinstance(content_element["content"], list):
                    continue
                for element_content_element in content_element["content"]:
                    if key in element_content_element.keys():
                        del element_content_element[key]
    return input_dict

def test_csv_file_parser(global_var):
    test_fname = "tests/data/example.csv"
    compare_fname = "tests/data/csv.json"
    example_dict = dict()
    parser = CsvToDictParser(word_count_limit=pytest.csv_word_count_limit)
    with open(compare_fname) as fp:
        example_dict = json.load(fp)
    out_dict = parser.parse_file(test_fname)
    out_dict = delete_key_from_content(out_dict, "id")
    example_dict = delete_key_from_content(example_dict, "id")
    out_dict = delete_key_from_content(out_dict, "timestamp")
    example_dict = delete_key_from_content(example_dict, "timestamp")
    assert out_dict == example_dict

def test_csv_bytes_parser(global_var):
    test_fname = "tests/data/example.csv"
    compare_fname = "tests/data/csv.json"
    example_dict = dict()
    parser = CsvToDictParser(word_count_limit=pytest.csv_word_count_limit)
    with open(compare_fname) as fp:
        example_dict = json.load(fp)
    with open(test_fname, 'rb') as fp:
        input_bytes = fp.read()
        out_dict = parser.parse_bytes(input_bytes)
        out_dict = delete_key_from_content(out_dict, "id")
        example_dict = delete_key_from_content(example_dict, "id")
        out_dict = delete_key_from_content(out_dict, "timestamp")
        example_dict = delete_key_from_content(example_dict, "timestamp")
        assert out_dict == example_dict

def test_docx_file_parser(global_var):
    test_fname = "tests/data/example.docx"
    compare_fname = "tests/data/docx.json"
    example_dict = dict()
    parser = DocxToDictParser(word_count_limit=pytest.docx_word_count_limit)
    with open(compare_fname) as fp:
        example_dict = json.load(fp)
    out_dict = parser.parse_file(test_fname)
    out_dict = delete_key_from_content(out_dict, "id")
    example_dict = delete_key_from_content(example_dict, "id")
    out_dict = delete_key_from_content(out_dict, "timestamp")
    example_dict = delete_key_from_content(example_dict, "timestamp")
    assert out_dict == example_dict

def test_docx_bytes_parser(global_var):
    test_fname = "tests/data/example.docx"
    compare_fname = "tests/data/docx.json"
    example_dict = dict()
    parser = DocxToDictParser(word_count_limit=pytest.docx_word_count_limit)
    with open(compare_fname) as fp:
        example_dict = json.load(fp)
    with open(test_fname, 'rb') as fp:
        input_bytes = fp.read()
        out_dict = parser.parse_bytes(input_bytes)
        out_dict = delete_key_from_content(out_dict, "id")
        example_dict = delete_key_from_content(example_dict, "id")
        out_dict = delete_key_from_content(out_dict, "timestamp")
        example_dict = delete_key_from_content(example_dict, "timestamp")
        assert out_dict == example_dict

def test_email_file_parser(global_var):
    test_fname = "tests/data/example.eml"
    compare_fname = "tests/data/email.json"
    example_dict = dict()
    parser = EmailToDictParser(word_count_limit=pytest.email_word_count_limit)
    with open(compare_fname) as fp:
        example_dict = json.load(fp)
    out_dict = parser.parse_file(test_fname)
    out_dict = delete_key_from_content(out_dict, "id")
    example_dict = delete_key_from_content(example_dict, "id")
    out_dict = delete_key_from_content(out_dict, "timestamp")
    example_dict = delete_key_from_content(example_dict, "timestamp")
    assert out_dict == example_dict

def test_email_bytes_parser(global_var):
    test_fname = "tests/data/example.eml"
    compare_fname = "tests/data/email.json"
    example_dict = dict()
    parser = EmailToDictParser(word_count_limit=pytest.email_word_count_limit)
    with open(compare_fname) as fp:
        example_dict = json.load(fp)
    with open(test_fname, 'rb') as fp:
        input_bytes = fp.read()
        out_dict = parser.parse_bytes(input_bytes)
        out_dict = delete_key_from_content(out_dict, "id")
        example_dict = delete_key_from_content(example_dict, "id")
        out_dict = delete_key_from_content(out_dict, "timestamp")
        example_dict = delete_key_from_content(example_dict, "timestamp")
        assert out_dict == example_dict

def test_pdf_file_parser(global_var):
    test_fname = "tests/data/example.pdf"
    compare_fname = "tests/data/pdf.json"
    example_dict = dict()
    parser = PdfToDictParser(word_count_limit=pytest.pdf_word_count_limit)
    with open(compare_fname) as fp:
        example_dict = json.load(fp)
    out_dict = parser.parse_file(test_fname)
    out_dict = delete_key_from_content(out_dict, "id")
    example_dict = delete_key_from_content(example_dict, "id")
    out_dict = delete_key_from_content(out_dict, "timestamp")
    example_dict = delete_key_from_content(example_dict, "timestamp")
    assert out_dict == example_dict

def test_pdf_bytes_parser(global_var):
    test_fname = "tests/data/example.pdf"
    compare_fname = "tests/data/pdf.json"
    example_dict = dict()
    parser = PdfToDictParser(word_count_limit=pytest.pdf_word_count_limit)
    with open(compare_fname) as fp:
        example_dict = json.load(fp)
    with open(test_fname, 'rb') as fp:
        input_bytes = fp.read()
        out_dict = parser.parse_bytes(input_bytes)
        out_dict = delete_key_from_content(out_dict, "id")
        example_dict = delete_key_from_content(example_dict, "id")
        out_dict = delete_key_from_content(out_dict, "timestamp")
        example_dict = delete_key_from_content(example_dict, "timestamp")
        assert out_dict == example_dict

def test_txt_file_parser(global_var):
    test_fname = "tests/data/example.txt"
    compare_fname = "tests/data/txt.json"
    example_dict = dict()
    parser = TxtToDictParser(word_count_limit=pytest.txt_word_count_limit)
    with open(compare_fname) as fp:
        example_dict = json.load(fp)
    out_dict = parser.parse_file(test_fname)
    out_dict = delete_key_from_content(out_dict, "id")
    example_dict = delete_key_from_content(example_dict, "id")
    out_dict = delete_key_from_content(out_dict, "timestamp")
    example_dict = delete_key_from_content(example_dict, "timestamp")
    assert out_dict == example_dict

def test_txt_bytes_parser(global_var):
    test_fname = "tests/data/example.txt"
    compare_fname = "tests/data/txt.json"
    example_dict = dict()
    parser = TxtToDictParser(word_count_limit=pytest.txt_word_count_limit)
    with open(compare_fname) as fp:
        example_dict = json.load(fp)
    with open(test_fname, 'rb') as fp:
        input_bytes = fp.read()
        out_dict = parser.parse_bytes(input_bytes)
        out_dict = delete_key_from_content(out_dict, "id")
        example_dict = delete_key_from_content(example_dict, "id")
        out_dict = delete_key_from_content(out_dict, "timestamp")
        example_dict = delete_key_from_content(example_dict, "timestamp")
        assert out_dict == example_dict

def test_xlsx_file_parser(global_var):
    test_fname = "tests/data/example.xlsx"
    compare_fname = "tests/data/xlsx.json"
    example_dict = dict()
    parser = XlsxToDictParser(word_count_limit=pytest.xlsx_word_count_limit)
    with open(compare_fname) as fp:
        example_dict = json.load(fp)
    out_dict = parser.parse_file(test_fname)
    out_dict = delete_key_from_content(out_dict, "id")
    example_dict = delete_key_from_content(example_dict, "id")
    out_dict = delete_key_from_content(out_dict, "timestamp")
    example_dict = delete_key_from_content(example_dict, "timestamp")
    assert out_dict == example_dict

def test_xlsx_bytes_parser(global_var):
    test_fname = "tests/data/example.xlsx"
    compare_fname = "tests/data/xlsx.json"
    example_dict = dict()
    parser = XlsxToDictParser(word_count_limit=pytest.xlsx_word_count_limit)
    with open(compare_fname) as fp:
        example_dict = json.load(fp)
    with open(test_fname, 'rb') as fp:
        input_bytes = fp.read()
        out_dict = parser.parse_bytes(input_bytes)
        out_dict = delete_key_from_content(out_dict, "id")
        example_dict = delete_key_from_content(example_dict, "id")
        out_dict = delete_key_from_content(out_dict, "timestamp")
        example_dict = delete_key_from_content(example_dict, "timestamp")
        assert out_dict == example_dict

def test_ner_file_parser(global_var):
    test_fname = "tests/data/example_ner_annotated.jsonl"
    compare_fname = "tests/data/parsed_ner_annotated.json"
    example_dict = dict()
    parser = NERAnnotatedJsonlToDictParser(word_count_limit=pytest.ner_word_count_limit)
    with open(compare_fname) as fp:
        example_dict = json.load(fp)
    out_dict = parser.parse_file(test_fname)
    out_dict = delete_key_from_content(out_dict, "id")
    example_dict = delete_key_from_content(example_dict, "id")
    out_dict = delete_key_from_content(out_dict, "timestamp")
    example_dict = delete_key_from_content(example_dict, "timestamp")
    assert out_dict == example_dict

def test_ner_bytes_parser(global_var):
    test_fname = "tests/data/example_ner_annotated.jsonl"
    compare_fname = "tests/data/parsed_ner_annotated.json"
    example_dict = dict()
    parser = NERAnnotatedJsonlToDictParser(word_count_limit=pytest.ner_word_count_limit)
    with open(compare_fname) as fp:
        example_dict = json.load(fp)
    with open(test_fname, 'rb') as fp:
        input_bytes = fp.read()
        out_dict = parser.parse_bytes(input_bytes)
        out_dict = delete_key_from_content(out_dict, "id")
        example_dict = delete_key_from_content(example_dict, "id")
        out_dict = delete_key_from_content(out_dict, "timestamp")
        example_dict = delete_key_from_content(example_dict, "timestamp")
        assert out_dict == example_dict

def test_squad_file_parser(global_var):
    test_fname = "tests/data/example_squad_annotated.json"
    compare_fname = "tests/data/parsed_squad_annotated.json"
    example_dict = dict()
    parser = SQuADAnnotatedJsonToDictParser(word_count_limit=pytest.squad_word_count_limit)
    with open(compare_fname) as fp:
        example_dict = json.load(fp)
    out_dict = parser.parse_file(test_fname)
    out_dict = delete_key_from_content(out_dict, "id")
    example_dict = delete_key_from_content(example_dict, "id")
    out_dict = delete_key_from_content(out_dict, "timestamp")
    example_dict = delete_key_from_content(example_dict, "timestamp")
    assert out_dict == example_dict

def test_squad_bytes_parser(global_var):
    test_fname = "tests/data/example_squad_annotated.json"
    compare_fname = "tests/data/parsed_squad_annotated.json"
    example_dict = dict()
    parser = SQuADAnnotatedJsonToDictParser(word_count_limit=pytest.squad_word_count_limit)
    with open(compare_fname) as fp:
        example_dict = json.load(fp)
    with open(test_fname, 'rb') as fp:
        input_bytes = fp.read()
        out_dict = parser.parse_bytes(input_bytes)
        out_dict = delete_key_from_content(out_dict, "id")
        example_dict = delete_key_from_content(example_dict, "id")
        out_dict = delete_key_from_content(out_dict, "timestamp")
        example_dict = delete_key_from_content(example_dict, "timestamp")
        assert out_dict == example_dict