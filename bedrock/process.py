import csv
import pandas as pd
from bedrock.processors.SpacyProcessor import SpacyProcessor
from bedrock.processors.NltkProcessor import NltkProcessor


# TODO: Refactor the DataFrame part


TEXT_ID = 'text_id'
SENTENCE_ID = 'sentence_id'
SENTENCE = 'sentence'
GROUND_TRUTH = 'ground_truth'
PROCESSED = 'processed'


def get_engine(engine_name, lang):
    # Get the processor instance and work with the methods directly
    engine_factory = {
        'spacy': SpacyProcessor,
        'nltk': NltkProcessor
    }
    engine = engine_factory[engine_name](lang)
    return engine


processor = get_engine(engine_name='spacy', lang='de')


def set_engine(engine_name='spacy', lang='de'):
    global processor
    processor = get_engine(engine_name, lang)


def sentence_tokenize(text_input):
    return processor.sentence_tokenize(text_input)


def lemmatize(text_input):
    return processor.lemmatize(text_input)


def stem(text_input):
    return processor.stem(text_input)


def tokenize(text_input):
    return processor.tokenize(text_input)


def remove_short(text_input, min_word_len):
    return processor.remove_short(text_input, min_word_len)


def replace_chars(text_input, chars_to_replace, replacement_char):
    return processor.replace_chars(text_input, chars_to_replace, replacement_char)


def viperize(text_input, vip_words):
    return processor.viperize(text_input, vip_words)


def pipeline(
        texts,
        min_word_len=5,
        do_stem=True,
        chars_to_remove=None,
        replacement_char=' ',
        vip_words=None,
        do_tokenize=False):
    # texts:
    #   list of texts
    # min_word_len:
    #   Removes words shorter than given value.
    # chars_to_remove:
    #   chars_to_remove=['-', '.'] and chars_to_remove='-.'
    #   does the same, removes '-' and '.' from bedrock.
    # replacement_char:
    #   If anything is given for remove chars it will
    # replacement_char:
    #   If anything is given for remove chars it will
    #   replace them with this character.
    # vip_words:
    #   Word patterns that will be appended to the end
    #   of the bedrock if found.
    #   e.g.
    #   ['karzinom', 'tumor', 'metastas', 'krebs', 'sarkom', 'malign']
    # do_tokenize:
    #   do_tokenize=True performs word tokenization and returns a
    #   list of tokens for each bedrock, making a function return
    #   list of lists.

    if processor is None:
        # Set to the default processor, if none is given.
        set_engine()

    texts = processor.replace_chars(texts, chars_to_remove, replacement_char)

    texts = processor.remove_short(texts, min_word_len)

    texts = processor.viperize(texts, vip_words)

    if do_stem:
        texts = processor.stem(texts)

    if do_tokenize:
        texts = processor.tokenize(texts)

    return texts


# TODO: make a generic function for both df and non-df inputs

def pipeline_df(
        df,
        field_name,
        persist_path=None,
        min_word_len=5,
        do_stem=True,
        chars_to_remove=None,
        replacement_char=' ',
        vip_words=None,
        do_tokenize=False):
    # Wrapper around the normal pipeline to use DataFrame as input
    # and return a DataFrame extended with the field 'processed'
    #
    # df:
    #   DataFrame containing the texts.
    # filed_name:
    #   Filed that contains texts in the DataFrame.

    df[PROCESSED] = pipeline(
        list(df[field_name]),
        min_word_len=min_word_len,
        do_stem=do_stem,
        chars_to_remove=chars_to_remove,
        replacement_char=replacement_char,
        vip_words=vip_words,
        do_tokenize=do_tokenize
    )

    if persist_path is not None:
        df.to_csv(persist_path)


def df_sentence_tokenize(text_id, text, ground_truth):
    # Sentence tokenization for DataFrame input
    result = []

    enumerated_sentences = enumerate(
        processor.sentence_tokenize(text)
    )

    for sentence_id, sentence in enumerated_sentences:
        result.append((text_id, sentence_id, sentence, ground_truth))
    return result


def index_tokenized_sentences(tokenized_sentences):
    # TODO: There is already a function that can do this, should be replaced
    word_dict = dict()
    x = []
    i = 0
    for tokenized_sentence in tokenized_sentences:
        indexed_sentence = []
        for word in tokenized_sentence:
            if word not in word_dict:
                i += 1
                word_dict[word] = i
            indexed_sentence.append(word_dict[word])
        x.append(indexed_sentence)
    return x, word_dict


def texts_to_sentences_df(
        texts,
        text_ids=None,
        ground_truths=None,
        columns=None,
        persist_path=None):

    if columns is None:
        columns = [
            TEXT_ID,
            SENTENCE_ID,
            SENTENCE,
            GROUND_TRUTH
        ]

    sentences_matrix = []
    # TODO: Possible changes:
    #  1. use real impression ids,
    #  2. use df as input. Probably need another function.

    if ground_truths is None:
        print('No ground truths supplied, making them up. Count:', len(texts))
        ground_truths = [''] * len(texts)

    if text_ids is None:
        text_ids = range(len(texts))

    inputs = zip(text_ids, texts, ground_truths)

    for text_id, text, ground_truth in inputs:
        sentences_matrix.extend(
            df_sentence_tokenize(
                text_id,
                text,
                ground_truth
            )
        )
    df = pd.DataFrame(sentences_matrix, columns=columns)

    if persist_path is not None:
        df.to_csv(persist_path, quoting=csv.QUOTE_NONNUMERIC)

    return df


def text_to_sentences(text, persist_path):
    # TODO: Obsolete, but still used in some playground code
    if processor is None:
        set_engine()

    return processor.sentence_tokenizer(text, persist_path=persist_path)