import configparser
from collections import namedtuple
import time
from os import path
import pickle
import glob


def config_to_namedtuple(config_path='config.ini'):
    _config = configparser.ConfigParser()
    _config.read(config_path)
    groups_dict = dict()
    for group_name in _config.keys():
        groups_dict[group_name] = namedtuple(group_name, _config[group_name].keys())(**_config[group_name])
    return namedtuple('Config', _config.keys())(**groups_dict)


def _timestamp():
    return time.strftime("%Y%m%d_%H%M%S")


def create_pickle_path(pickle_dir, base_name):
    return path.join(
        pickle_dir,
        _timestamp() + '_' + base_name + '.pickle'
    )


def save_pickle(model, path):
    if path is not None:
        with open(path, 'wb') as f:
            pickle.dump(model, f)


def load_pickle(pickle_path):
    with open(pickle_path, 'rb') as f:
        model = pickle.load(f)
    return model


def get_latest_file(dir_path):
    """Returns the name of the latest (most recent) file
    of the joined path(s)"""
    path.join(dir_path, '*')
    list_of_files = glob.iglob(dir_path)
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=path.getctime)
    _, filename = path.split(latest_file)
    return filename
