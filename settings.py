import os
import yaml


def load_config(fp):
    try:
        config = yaml.load(fp)
    except yaml.YAMLError as e:
        raise Exception("Failed to parse YAML: " + e.args[0])
    if not isinstance(config, dict):
        raise Exception("The YAML file must represent an object (a.k.a. hash, dict, map)")
    return config

DIR = os.path.abspath(os.path.dirname(__file__))
config = load_config(open(os.path.join(DIR, 'conf', 'general.yml')))
