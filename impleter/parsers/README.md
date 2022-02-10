# WordStash - Parsers

## What Does It Do
The sub-repository contains code related to WordStash's data parsing API. Textual documents are ingested, and chunked json payload representations of the documents are created during this stage. The system is compatible with the following file formats:
- CSV files
- Word documents (docx)
- Emails (eml) and attachments that fall in the allowed file formats
- PDFs
- Text files (txt)
- Excel spreadsheets (excel)

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