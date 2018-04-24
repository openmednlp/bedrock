import matplotlib.pyplot as plt
import numpy as np
import itertools
import texttable
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from wordcloud import WordCloud
from PIL import Image
from os import path
from bedrock import process


def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


def plot_confusion_reports(y, y_hat, class_names=None):
    if class_names is None:
        class_names = list(set(y).union(set(y_hat)))

    # Compute confusion matrix
    cnf_matrix = confusion_matrix(y, y_hat)
    np.set_printoptions(precision=2)

    # Plot non-normalized confusion matrix
    plt.figure()
    plot_confusion_matrix(cnf_matrix, classes=class_names,
                          title='Confusion matrix, without normalization')

    # Plot normalized confusion matrix
    plt.figure()
    plot_confusion_matrix(cnf_matrix, classes=class_names, normalize=True,
                          title='Normalized confusion matrix')

    plt.show()


def print_spacy_doc(doc):
    t = texttable.Texttable()
    print(doc.ents)
    t.add_row(['bedrock', 'lemma_', 'pos_', 'tag_', 'dep_', 'shape_', 'alpha', 'stop'])
    for token in doc:
        t.add_row(
            [
                token.text,
                token.lemma_,
                token.pos_,
                token.tag_,
                token.dep_,
                token.shape_,
                token.is_alpha,
                token.is_stop,
            ]
        )
    print(t.draw())


def show_stats(y, y_hat):
    decision_labels = list(set(y_hat).union(set(y)))

    stat_names = ['precission', 'recall', 'f1', 'count']
    stats = precision_recall_fscore_support(
        y,
        y_hat,
        average=None,
        labels=decision_labels
    )

    print(('{}' + '{:>8}'*len(decision_labels)).format(' '*15, *decision_labels))
    print('-'*35)
    for stat_name, class_stat_values in zip(stat_names, stats):
        print(
            ('{:>15}  |' + '  {:05.2f} '*len(class_stat_values))
             .format(stat_name, *class_stat_values)
        )

    print('Done')


def word_cloud(text, show_plot=True, mask_path=None, save_path=None):
    # TODO: not tested as function
    mask = None
    if mask_path:
        mask = np.array(
            Image.open(mask_path)
        )

    wc = WordCloud(width=512, height=512, background_color="white", max_words=100, mask=mask)
    wc.generate(text)

    if save_path:
        wc.to_file(save_path)

    if show_plot:
        plt.figure()
        plt.imshow(wc)
        plt.show()


def _df_to_text(
        df, show_column,
        filter_column,
        condition_list,
        min_word_len):

    df_filtered = df[
        df[filter_column].isin(condition_list)
    ]

    text = ' '.join(df_filtered[show_column])

    processor = process.get_engine()
    text = processor.remove_short([text], min_word_len)
    text = processor.stem(text)

    return text[0]


def word_clouds(df, save_dir=None):
    filters = [
        [4, 5],
        [1, 2],
        [0, 3]]

    for filter_values in filters:
        text = _df_to_text(
            df, 'sentence', 'ground_truth', filter_values, 5
        )
        name_part = '_'.join([str(v) for v in filter_values])
        save_path = save_dir
        if save_dir:
            save_path = path.join(
                save_dir,
                name_part + '_filtered.png'
            )
        word_cloud(text, save_path=save_path)