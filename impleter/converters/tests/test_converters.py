from src.converters import (
    TEXT_KEY,
    SENTENCE1_KEY,
    CONTEXT_KEY,
    DATA_KEY,
    PARAGRAPHS_KEY,
    LABEL_KEY,
    QAS_KEY,
    QUESTION_KEY,
    ANSWERS_KEY,
    ANSWER_START_KEY,
    ClassificationCrudeToLabel,
    NerCrudeToLabel,
    NerLabelToTrain,
    SquadCrudeToLabel,
    SquadLabelToTrain

)

TEST_PAYLOAD = {
    "id": "57639482-160721-1931",
    "title": "Machine Learning Progress",
    "content": "The field of machine learning has made tremendous progress over the past decade"
}

def test_classification():
    label = "scientific_context"
    test_dict = TEST_PAYLOAD.copy()
    test_dict.update({LABEL_KEY: label})
    converter = ClassificationCrudeToLabel()
    out_list = converter.convert_list([test_dict])
    sentence = out_list[-1][SENTENCE1_KEY]
    label = out_list[-1][LABEL_KEY]
    assert len(out_list) == 1
    assert sentence == test_dict["content"]
    assert label == test_dict[LABEL_KEY]

def test_ner():
    labels = [[4, 9, "U-LOC"]]
    compare_out_labels = ['O', 'U-LOC', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']
    test_dict = TEST_PAYLOAD.copy()
    test_dict.update({LABEL_KEY: labels})
    converter = NerCrudeToLabel()
    out_list = converter.convert_list([test_dict])
    assert len(out_list) == 1
    assert out_list[-1][TEXT_KEY] == test_dict["content"]
    str_labels = [[str(elem) for elem in label] for label in labels if len(label) == 3]
    assert out_list[-1][LABEL_KEY] == str_labels
    converter = NerLabelToTrain()
    out_label_list = converter.convert_list(out_list)
    out_labels = out_label_list[-1][LABEL_KEY]
    assert out_labels == compare_out_labels

def test_squad():
    qas = [{"question": "What has made progress?", "answers":[{"answer_start": 0, "text": "The field of machine learning has made tremendous progress over the past decade"}]}]
    test_dict = TEST_PAYLOAD.copy()
    converter = SquadCrudeToLabel()
    out_list = converter.convert_list([test_dict])
    assert len(out_list[-1][DATA_KEY]) == 1
    assert out_list[-1][DATA_KEY][0][PARAGRAPHS_KEY][0][CONTEXT_KEY] == test_dict["content"]
    out_list[-1][DATA_KEY][0][PARAGRAPHS_KEY][0][QAS_KEY] = qas
    converter = SquadLabelToTrain()
    out_train_list = converter.convert_list(out_list)
    question = out_train_list[-1][DATA_KEY][0][DATA_KEY][0][QUESTION_KEY]
    answer_start = out_train_list[-1][DATA_KEY][0][DATA_KEY][0][ANSWERS_KEY][ANSWER_START_KEY][0]
    text = out_train_list[-1][DATA_KEY][0][DATA_KEY][0][ANSWERS_KEY][TEXT_KEY][0]
    assert question == qas[0]["question"]
    assert answer_start == qas[0]["answers"][0]["answer_start"]
    assert text == qas[0]["answers"][0]["text"]