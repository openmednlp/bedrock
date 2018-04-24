from os import path, listdir
import pandas as pd
from nltk import edit_distance
import csv
from sklearn.model_selection import train_test_split
from bedrock import processors


TEXT_ID = 'text_id'
TEXT = 'text'
SENTENCE_ID = 'sentence_id'
SENTENCE = 'sentence'
GROUND_TRUTH = 'ground_truth'
PROCESSED = 'processed'


def _get_file_type(data_path):
    _, file_type = path.splitext(data_path)
    return str.lower(file_type)


def file_to_df(data_path):
    file_type = _get_file_type(data_path)

    if file_type == '.csv':
        return pd.read_csv(data_path)
    else:
        raise NotImplementedError('This file type is not supported')


def _get_report_paths(dir_path):
    return [
        path.join(dir_path, file_name)
        for file_name in listdir(dir_path)
        if path.isfile(
            path.join(dir_path, file_name)
        )
           and (
                   path.splitext(file_name)[1] == '.txt'
           )
    ]


def extract_impression_from_text(text):
    #TODO: domain specific, move to propper location

    impression_found = False
    impression_extracted = False
    impression_lines = []

    for line in text.splitlines():
        if not impression_found:
            # TODO: maybe use similarity measure in case there is a typo
            if edit_distance(line.strip().lower(), 'beurteilung') < 3:
                impression_found = True
            continue

        if impression_extracted:
            break

        # TODO: maybe use similarity measure in case there is a typo
        line_is_empty = line.strip().lower() == ''
        new_text_segment_detected = edit_distance(
            line.strip().lower(), 'beilagen zum befund'
        )
        if new_text_segment_detected < 3 or line_is_empty:
            impression_extracted = True
            continue

        impression_lines.append(line)

    impression = None
    if len(impression_lines) > 0:
        impression = '\n'.join(impression_lines)

    return impression


def extract_impression_from_file(file_path):
    # TODO: domain specific, move to propper location
    with open(file_path, "r", encoding='utf8') as f:
        text = f.read()

    return extract_impression_from_text(text)


def extract_impressions_from_files(
    #TODO: domain specific, move to propper location
        reports_dir_path,
        persist_path=None):

    report_paths = _get_report_paths(reports_dir_path)

    text_ids = []
    texts = []

    for file_path in report_paths:
        impression = extract_impression_from_file(file_path)
        if impression is None:
            continue
        texts.append(impression)
        text_ids.append(path.basename(file_path).split('-')[0])

    df = pd.DataFrame(
        {
            TEXT_ID: text_ids,
            TEXT: texts
        }
    )

    if persist_path is not None:
        df.to_csv(persist_path, quoting=csv.QUOTE_NONNUMERIC)

    return df


def balance_df(df, balance_type='random_upsample'):
    if balance_type is None:
        print('balance: no type defined, exiting...')
        return df

    positive_count = sum(df.binary_class)
    negative_count = len(df) - positive_count
    difference = abs(negative_count - positive_count)

    if difference < 2:
        print('balance: nothing to do, exiting...')
        return df

    if balance_type.lower() == 'random_upsample':
        is_positive_dominant = positive_count > negative_count
        if is_positive_dominant:
            minority = df[df.binary_class]
        else:
            minority = df[~df.binary_class]

        upsampled = minority.sample(n=difference, replace=True)
        return df.append(upsampled, ignore_index=True)

    raise ValueError('Wrong balancing type')


def train_validate_split_df(
        df,
        input_field_name,
        target_field_name,
        split_by_field,
        test_size=0.3,
        random_state=None):

    df_grouped = df.groupby(split_by_field)
    input_ids = list(df_grouped.groups.keys())
    group_max_targets = list(df_grouped[target_field_name].max())

    train_ids, test_ids, _, _ = train_test_split(
        input_ids,
        group_max_targets,
        test_size=test_size,
        random_state=random_state,
        # stratify=group_max_targets # Assumption: data is balanced
        # TODO: cannot stratify if there is only one sample
    )

    train_dataset = df[
        df[split_by_field].isin(train_ids)
    ]
    test_dataset = df[
        df[split_by_field].isin(test_ids)
    ]

    return (train_dataset[input_field_name],
            test_dataset[input_field_name],
            train_dataset[target_field_name],
            test_dataset[target_field_name]
            )


def reports_to_train_test(reports_dir, persist_path=None):
    # This does not make sense, because there are no targets given,
    # but is a good example of the whole process.

    df_impressions = extract_impressions_from_files(reports_dir, persist_path)

    # TODO: Needs new persist path
    df_sentences = processors.text_to_sentences(
        df_impressions[TEXT],
        persist_path
    )

    # TODO: Needs new persist path
    processors.pipeline_df(
        df_sentences,
        SENTENCE,
        persist_path
    )

    return train_validate_split_df(
        df_sentences,
        PROCESSED,
        GROUND_TRUTH,
        SENTENCE_ID
    )