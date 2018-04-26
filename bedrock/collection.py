from os import path, listdir
import pandas as pd
from nltk import edit_distance
import csv
from sklearn.model_selection import train_test_split

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


def get_file_paths(dir_path, extensions=('.txt',)):
    return [
        path.join(dir_path, file_name)
        for file_name in listdir(dir_path)
        if path.isfile(path.join(dir_path, file_name))
        and (path.splitext(file_name)[1] in extensions)
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

    report_paths = get_file_paths(reports_dir_path)

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


def _detect_header(line, headers):
    for header in headers:
        header_diff = edit_distance(
            line, header
        )
        is_header = header_diff < 3
        if is_header:
            return header
    return None


def section_label(
        text_lines,
        headers,
        case_sensitive=False,
        header_label='header',
        default_label='n/a',
        empty_label='n/a'):
    # Input a text_lines or list of text_lines lines and get back labels for each line.
    current_label = default_label
    max_label_len = max([len(w) for w in headers])

    if not case_sensitive:
        headers = [h.lower() for h in headers]
    if type(text_lines) is not list:
        text_lines = text_lines.splitlines()

    labels = []
    for line in text_lines:
        line = line.strip()
        if not line:
            labels.append(empty_label)
            continue

        if not case_sensitive:
            line = line.lower()

        # No need to look if a line is longer than the longest header
        # Extending the len by 2 as a tolerance for characters like ':'
        if len(line) > max_label_len + 2:
            labels.append(current_label)
            continue

        new_label = _detect_header(line, headers)
        if new_label is None:
            labels.append(current_label)
            continue

        current_label = new_label
        labels.append('{} {}'.format(header_label, current_label))

    return labels


def section_label_file(
        file_path,
        headers,
        case_sensitive=False,
        header_label='header',
        default_label='n/a',
        empty_label='n/a'):
    # Read file and label text by section
    with open(file_path, "r", encoding='utf8') as f:
        text = f.read()

    text_lines = text.splitlines()

    labels = section_label(
        text_lines,
        headers,
        case_sensitive,
        header_label,
        default_label,
        empty_label
    )

    return text_lines, labels


def section_label_dir(
        dir_path,
        headers,
        case_sensitive=False,
        header_label='header',
        default_label='n/a',
        empty_label='n/a',
        extensions=('.txt',)):
    # Read files from dir and label text by section
    file_paths = get_file_paths(dir_path, extensions)

    text_ids = []
    text_lists = []
    text_list_labels = []
    for file_path in file_paths:
        text_ids.append(path.basename(file_path))
        text_list, labels = section_label_file(
            file_path,
            headers,
            case_sensitive,
            header_label,
            default_label,
            empty_label)
        text_lists.append(text_list)
        text_list_labels.append(labels)

    return text_ids, text_lists, text_list_labels


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
