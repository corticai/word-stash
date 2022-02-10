# WordStash - Converters

## What Does It Do
The sub-repository contains code related to WordStash's data conversion API that creates the following machine learning data formats:
- [Text classification](https://developers.google.com/machine-learning/guides/text-classification)
- [Extractive question answering (SQuAD)](https://rajpurkar.github.io/SQuAD-explorer/)
- Part of Speech tagging formats:
    - [BILUO](https://towardsdatascience.com/extend-named-entity-recogniser-ner-to-label-new-entities-with-spacy-339ee5979044)
    - [Named Entity Recognition](https://cs230.stanford.edu/blog/namedentity/)

## Prerequisites
The following is required to run the code locally:

1. [Docker 19.03 or above - Download Docker](https://www.docker.com/products/docker-desktop)
1. [Docker Compose 1.27 or above - (Note that Docker for MacOS comes with Docker Compose)](https://docs.docker.com/compose/)
1. [GNU Make (which is pre-installed on MacOs and Linux)](https://www.gnu.org/software/make/)
1. [Python 3.8 or above (with Pip)](https://www.python.org/downloads/)
1. [AWS command line interface](https://aws.amazon.com/cli/)

## Instructions To Test the Code Locally
To run the tests locally, execute the following command in the converters directory:
```
make test
```