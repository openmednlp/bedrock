# Bedrock
[![Build Status](https://travis-ci.org/openmednlp/bedrock.svg?branch=master)](https://travis-ci.org/openmednlp/bedrock)

## You have discovered bedrock

__Bedrock__ is a high-level text pre-processing API,
written in Python and can run on Spacy as its backend.
It allows you to quickly perform the text processing groundwork without having.
It does the menial work, so you don't have to.

Use this library if you find the following highlights useful:
* Fast prototyping
* Switching between different backends
* Work in batches, rather than writing loops
* Support for DataFrame and CAS xmi inputs/outputs

Install __bedrock__ in a jiffy:
```bash
pip install bedrock
bedrock download de
```

## From zero to bedrock hero in 10 seconds

Now you can run

```python
from bedrock.pipeline import Pipeline
Pipeline(language='de').parse_text("Hello world").get_docs()
```

Congrats! :tada:

## Engines and Languages

Currently __bedrock__ supports spacy as its background engine.

And the following languages and corresponding download arguments:
* English ('en' or 'english')
* German ('de', 'german' or 'deutsch')
* German ('fr' or 'french')

## Installation and usage
Package installation
```bash
pip install bedrock
```

Install support for all languages:
```bash
bedrock download all
```

Install support only for English:
```bash
bedrock download en
```

Install support for German:
```bash
bedrock download de
```

Install support for French:
```bash
bedrock download fr
```

Import modules from package in your code:
```python
from bedrock.pipeline import Pipeline                        # Processing texts
from bedrock.annotator.annotator import Annotator            # Annotator interface
from bedrock.annotator.dictionary_annotator import DictionaryAnnotator # Prebuilt dictionary annotator
from bedrock.annotator.regex_annotator import RegexAnnotator # Prebuild regex annotator
```
