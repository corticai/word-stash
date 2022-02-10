""" Payload conversion - File containing functionality that converts JSON payload representations into machine learning compatible formats.

The payload representations are then transformed into one of the following machine learning formats:
- Text classification
- Extractive question answering (SQuAD)
- Part of Speech tagging formats:
    - BILUO
    - Named Entity Recognition

    Typical usage example:
        from converters import ClassificationCrudeToLabel
        example_dict = {
            "id": "57639482-160721-1931",
            "title": "Machine Learning Progress",
            "content": "The field of machine learning has made tremendous progress over the past decade"
        }
        converter = ClassificationCrudeToLabel()
        out_dict = converter.convert(example_dict)
"""
import abc
from uuid import uuid4
from typing import List, Dict
from datetime import datetime
from spacy.util import get_lang_class
from spacy.training import offsets_to_biluo_tags

ML_FILE_DATETIME = "%Y%m%d_%H%M%S"
ID_KEY = "id"
DATA_KEY = "data"
TITLE_KEY = "title"
PARAGRAPHS_KEY = "paragraphs"
CONTENT_KEY = "content"
CONTENT1_KEY = "content1"
CONTENT2_KEY = "content2"
SENTENCE1_KEY = "sentence1"
SENTENCE2_KEY = "sentence2"
CONTEXT_KEY = "context"
QAS_KEY = "qas"
QUESTION_KEY = "question"
ANSWERS_KEY = "answers"
ANSWER_START_KEY = "answer_start"
TEXT_KEY = "text"
VERSION_KEY = "version"
LABEL_KEY = "label"


def create_file_datetime() -> str:
    """function that generates a file date time
    Returns:
        str: String in a yyyymmdd_hhmmss format
    """
    return str(uuid4()) + "-" + datetime.now().strftime(ML_FILE_DATETIME)

class AbstractConverter(object):
    """AbstractConverter"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def convert_list(self, input_list:List[Dict]):
        """convert_list"""
        return

    @abc.abstractmethod
    def convert(self, input_dict:Dict):
        """convert"""
        return


class ClassificationCrudeToLabel(AbstractConverter):
    """Raw (crude) dictionary to classification converter.

    Attributes:
        id_key: A string type key name of the payload's unique id.
        content1_key: A string type key name of the payload's content.
        content2_key: A string type key name of the payload's second content. This value is not null if classification is based on a value comparison of content1_key and content2_key (http://www.nlp.town/blog/sentence-similarity/).
        label_key: A sring type key name for the classification label.
        output_list: List type that contains the converted input_dict_list.
    """
    def __init__(self, id_key:str=ID_KEY, content1_key:str=CONTENT_KEY, content2_key:str=None, label_key:str=LABEL_KEY):
        self.id_key = id_key
        self.content1_key = content1_key
        self.content2_key = content2_key
        self.label_key = label_key
        self.output_list = []

    def convert_list(self, input_dict_list:List[Dict]) -> List[Dict]:
        """Converts a list of raw (crude) dictionaries to a list of classification dictionaries.

        Args:
        input_dict_list: Input list of crude dictionaries

        Returns:
        List of classification dictionaries.

        Raises:
        """
        for input_dict in input_dict_list:
            paragraph = self.convert(input_dict)
            self.output_list.append(paragraph)
        return self.output_list

    def convert(self, input_dict:Dict) -> Dict:
        """Converts a raw (crude) dictionary to a classification dictionary.

        Args:
        input_dict: Input crude dictionary

        Returns:
        Classification dictionary.

        Raises:
        """
        paragraph = {ID_KEY: input_dict.get(self.id_key, None)}
        for key, value in input_dict.items():
            if key not in [self.id_key, self.content1_key, self.content2_key]:
                paragraph[key] = value
        paragraph.update({ 
            SENTENCE1_KEY: input_dict.get(self.content1_key, None),
            SENTENCE2_KEY: input_dict.get(self.content2_key, None),
            LABEL_KEY: input_dict.get(self.label_key, None) })
        return paragraph

class NerCrudeToLabel(AbstractConverter):
    """Raw (crude) dictionary to named entity recognition (NER) BILUO dictionary converter.

    Attributes:
        id_key: A string type key name of the payload's unique id.
        content_key: A string type key name of the payload's content.
        label_key: A sring type key name for the NER BILUO labels.
        output_list: List type that contains the converted input_dict_list.
    """
    def __init__(self, id_key:str=ID_KEY, content_key:str=CONTENT_KEY, label_key:str=LABEL_KEY):
        self.id_key = id_key
        self.content_key = content_key
        self.label_key = label_key
        self.output_list = []

    def convert_list(self, input_dict_list:List[Dict]) -> List[Dict]:
        """Converts a list of raw (crude) dictionaries to a list of NER BILUO dictionaries.

        Args:
        input_dict_list: Input list of crude dictionaries

        Returns:
        List of NER BILUO dictionaries.

        Raises:
        """
        for input_dict in input_dict_list:
            paragraph = self.convert(input_dict)
            self.output_list.append(paragraph)
        return self.output_list

    def convert(self, input_dict:Dict) -> Dict:
        """Converts a raw (crude) dictionary to a NER BILUO dictionary.

        Args:
        input_dict: Input crude dictionary

        Returns:
        NER BILUO dictionary.

        Raises:
        """
        paragraph = {ID_KEY: input_dict.get(self.id_key, None)}
        for key, value in input_dict.items():
            if key not in [self.id_key, self.content_key]:
                paragraph[key] = value
        labels = input_dict.get(self.label_key, [])
        if len(labels) > 0:
            labels = [[str(elem) for elem in label] for label in labels if len(label) == 3]
        paragraph.update({
            TEXT_KEY: input_dict.get(self.content_key, None),
            LABEL_KEY: labels})
        return paragraph

class NerLabelToTrain(AbstractConverter):
    """BILUO to Hugging Face Transformer named entity recognition (NER) tokenised dictionary converter.

    Attributes:
        lang: A string type for language contained in the content_key - English (en) by default.
        id_key: A string type key name of the payload's unique id.
        content_key: A string type key name of the payload's content.
        label_key: A sring type key name for the NER BILUO labels.
        output_list: List type that contains the converted input_dict_list.
    """
    def __init__(self, lang:str="en", text_key:str=TEXT_KEY, label_key:str=LABEL_KEY):
        self.narrative_text = None
        self.doc = None
        cls = get_lang_class(lang)
        self.nlp = cls()
        self.text_key = text_key
        self.label_key = label_key
        self.output_list = []

    def convert_list(self, input_list:List[Dict]) -> List[Dict]:
        """Converts a list of NER BILUO dictionaries to a list of Hugging Face Transformer NER tokenised dictionaries.

        Args:
        input_dict_list: Input list of NER BILUO dictionaries

        Returns:
        List of NER tokenised dictionaries.

        Raises:
        """
        for input_dict in input_list:
            self.output_list.append(self.convert(input_dict))
        return self.output_list

    def convert(self, input_dict:Dict) -> Dict:
        """Converts a NER BILUO dictionary to a Hugging Face NER tokenised dictionary.

        Args:
        input_dict: Input NER BILUO dictionary

        Returns:
        NER tokenised dictionary.

        Raises:
        """
        narrative_text = input_dict[self.text_key]
        labels = input_dict[self.label_key]
        if len(labels) > 0:
            labels = [[int(elem) if i<2 and isinstance(elem, str) else elem for i, elem in enumerate(label)] for label in labels if len(label) == 3]
        doc = self.nlp(narrative_text)
        tags = offsets_to_biluo_tags(doc, labels)
        doc_list = [i.text for i in doc]
        tags = ['-'.join(i.split('-')[1:]) if len(i.split('-')) > 2 else i for i in tags]
        out_dict = {self.text_key: doc_list, self.label_key: tags}
        for key, value in input_dict.items():
            if key not in [self.text_key, self.label_key]:
                out_dict[key] = value
        return out_dict

class SquadCrudeToLabel(AbstractConverter):
    """Raw (crude) dictionary to Question Answer annotator dictionary converter.
    
    More details of the output payload format:
        - https://www.tensorflow.org/datasets/catalog/squad#:~:text=Stanford%20Question%20Answering%20Dataset%20(SQuAD,the%20question%20might%20be%20unanswerable.
    Attributes:
        id_key: A string type key name of the payload's unique id.
        title_key: A sring type key name for the payload's title.
        content_key: A string type key name of the payload's content.
        output_list: List type that contains the converted input_dict_list.
    """
    def __init__(self, id_key:str=ID_KEY, title_key:str=TITLE_KEY, content_key:str=CONTENT_KEY):
        self.id_key = id_key
        self.title_key =title_key
        self.content_key = content_key
        self.output_list = []

    def convert_list(self, input_dict_list:List[Dict]) -> List[Dict]:
        """Converts a list of crude/raw dictionaries to a list of SQuAD dictionaries.

        Args:
        input_dict_list: Input list of crude/raw dictionaries.

        Returns:
        List of SQuAD dictionaries.

        Raises:
        """
        title =None
        data = []
        paragraphs = []
        for input_dict in input_dict_list:
            if title != input_dict.get(self.title_key, None):
                if paragraphs:
                    data.append({TITLE_KEY: title, PARAGRAPHS_KEY: paragraphs})
                    paragraphs = []
                title =input_dict.get(self.title_key, None)
            paragraph = self.convert(input_dict)
            paragraphs.append(paragraph)
        if paragraphs:
            data.append({TITLE_KEY: title, PARAGRAPHS_KEY: paragraphs})
        self.output_list = [{VERSION_KEY: "v2.0", DATA_KEY: data}]
        return self.output_list

    def convert(self, input_dict:Dict) -> Dict:
        """Converts a crude/raw dictionary to a SQuAD dictionary.

        Args:
        input_dict: Input crude/raw dictionary.

        Returns:
        SQuAD dictionary.

        Raises:
        """
        paragraph = {ID_KEY: input_dict.get(self.id_key, None)}
        for key, value in input_dict.items():
            if key not in [self.id_key, self.content_key, LABEL_KEY]:
                paragraph[key] = value
        paragraph.update({
            CONTEXT_KEY: input_dict.get(self.content_key, None),
            QAS_KEY: input_dict.get(LABEL_KEY, []) })
        return paragraph

class SquadLabelToTrain(AbstractConverter):
    """SQuAD question-answer annotator dictionary to Hugging Face Transformer question-answer dictionary converter.
    
    More details of the input payload format:
        - https://www.tensorflow.org/datasets/catalog/squad#:~:text=Stanford%20Question%20Answering%20Dataset%20(SQuAD,the%20question%20might%20be%20unanswerable.
    Attributes:
        transformed_dict: A dictionary type that contains the converted payload.
        title_key: A sring type key name for the payload's title.
        output_list: List type that contains the converted input_dict_list.
    """
    def __init__(self):
        self.transformed_dict= dict()
        self.output_list = list()
        self.title = None

    def convert_list(self, input_list:List[Dict])  -> List[Dict]:
        """Converts a list of SQuAD question-answer annotator dictionaries to Hugging Face Transformer question-answer dictionaries.

        Args:
        input_dict_list: Input list of SQuAD question-answer annotator dictionaries.

        Returns:
        List of Hugging Face Transformer question-answer dictionaries.

        Raises:
        """
        train_list = []
        for input_dict in input_list:
            data_list = input_dict.get(DATA_KEY, None)
            for data_dict in data_list:
                self.title = data_dict.get(TITLE_KEY, None)
                paragraphs = data_dict.get(PARAGRAPHS_KEY, [])
                for paragraph in paragraphs:
                    qa_list = self.convert(paragraph)
                    train_list.append(qa_list)
            self.output_list = [{ DATA_KEY: train_list }]
        return self.output_list

    def convert(self, input_dict:Dict) -> Dict:
        """Converts a SQuAD question-answer annotator dictionary to a Hugging Face Transformer question-answer dictionary.

        Args:
        input_dict_list: Input of SQuAD question-answer annotator dictionary.

        Returns:
        Hugging Face Transformer question-answer dictionary.

        Raises:
        """
        output_list = []
        id_key = input_dict.get(ID_KEY, None)
        context = input_dict.get(CONTEXT_KEY, None)
        qas = input_dict.get(QAS_KEY, [])
        for i, qa in enumerate(qas):
            question = qa.get(QUESTION_KEY, None)
            question = question.lstrip().rstrip()
            answers = qa.get(ANSWERS_KEY, [])
            answer_start = []
            text = []
            for answer in answers:
                out_answer_start = answer.get(ANSWER_START_KEY, None)
                out_text = answer.get(TEXT_KEY)
                if not out_text:
                    continue
                answer_start.append(out_answer_start)
                text.append(out_text)
            existing_question_idx = next((index for (index, d) in enumerate(output_list) if d[QUESTION_KEY] == question), None)
            if existing_question_idx is not None:
                output_list[existing_question_idx][ANSWERS_KEY][ANSWER_START_KEY] = output_list[existing_question_idx][ANSWERS_KEY][ANSWER_START_KEY] + answer_start
                output_list[existing_question_idx][ANSWERS_KEY][TEXT_KEY] = output_list[existing_question_idx][ANSWERS_KEY][TEXT_KEY] + text
            else:
                squad_payload = {ID_KEY: id_key + "_" + create_file_datetime() + "_" + str(i), TITLE_KEY: self.title, CONTEXT_KEY: context, QUESTION_KEY: question, ANSWERS_KEY: {ANSWER_START_KEY: answer_start, TEXT_KEY: text}}
                for key, value in input_dict.items():
                    if key not in [ID_KEY, CONTEXT_KEY, QAS_KEY]:
                        squad_payload[key] = value                
                output_list.append(squad_payload)
        return {DATA_KEY: output_list}
