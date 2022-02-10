import distutils.log
from setuptools import setup, find_packages

distutils.log.set_verbosity(-1) # Disable logging in disutils
distutils.log.set_verbosity(distutils.log.DEBUG) # Set DEBUG level

setup(
    name='word-stash',
    version='1.0.0',
    author='Eugene Tan',
    author_email='eugene@corticai.com',
    description='NoamAI Natural Language Data Copia',
    package_dir={
        "converters": "./word-stash/impleter/converters/src",
        "parsers": "./word-stash/impleter/parsers/src",
        "publishers": "./word-stash/impleter/publishers/src"    
    },
    packages=[
        'word-stash',
        'word-stash/impleter',
        'word-stash/impleter/converters/src',
        'word-stash/impleter/parsers/src',
        'word-stash/impleter/publishers/src'
    ],
    include_package_data=True,
    package_data={'': ['*.json']},
    install_requires=[
        "pandas",
        "boto3",
        "pdfminer",
        "pdfplumber",
        "spacy",
        "pylatexenc",
        "opensearch-py",
        "requests",
        "requests-aws4auth"
    ],
)