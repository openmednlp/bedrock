# Bedrock
[![Build Status](https://travis-ci.org/openmednlp/bedrock.svg?branch=master)](https://travis-ci.org/openmednlp/bedrock)

## You have discovered bedrock

__Bedrock__ is a high-level text pre-processing API,
written in Python and can run on NLTK or Spacy as its backends.
It allows you to quickly perform the text processing groundwork without having.
It does the menial work, so you don't have to.

Use this library if you find the following highlights useful:
* Fast prototyping
* Switching between different backends
* Work in batches, rather than writing loops
* Support for DataFrame inputs/outputs

Install __bedrock__ in a jiffy:
```bash
pip install bedrock
bedrock download all
```

## From zero to bedrock hero in 10 seconds

Now you can run

```python
import bedrock
bedrock.process.pipeline('Hallo Welt')
```

Congrats! :tada:

## Engines and Languages

Currently __bedrock__ supports the following engines:
* spacy
* nltk

And the following languages and corresponding download arguments:
* English ('en' or 'english')
* German ('de', 'german' or 'deutsch')

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

Import modules from package in your code:
```python
from bedrock import process    # Processing texts
from bedrock import collection # Loading data collections
from bedrock import common     # Some common functions
from bedrock import feature    # Feature extraction
from bedrock import viz        # Visualizations
```
