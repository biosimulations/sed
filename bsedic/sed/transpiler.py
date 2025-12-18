import csv
import json
import pandas as pd

# TODO: need to import the database
#   containing information about the
#   different task types and their
#   available inputs and outputs

# TODO: provide a way to validate the
#   document directly without needing to
#   actually run it (???)


def load_csv(location, parameters=None):
    # TODO: deal with parameters (!)
    df = pd.read_csv(location)
    return df


MEDIA_TYPES = {
    "http://purl.org/NET/mediatypes/text/csv": load_csv}


def load_data(data_config):
    # TODO: deal with all error handling (!)

    location = data_config['location']
    format = data_config['format']
    parameters = data_config.get('parameters')
    load_data = MEDIA_TYPES[format]
    data = load_data(location, parameters)

    return data


def load_data_section(data_section_config):
    data = {}
    for key, config in data_section_config.items():
        loaded = load_data(config)
        data[key] = loaded

    import ipdb; ipdb.set_trace()

    return data

def transpile(sed):
    inputs = sed.get('inputs', {})
    data = inputs.get('data', {})
    models = inputs.get('models', {})

    tasks = sed.get('tasks', {})

    outputs = sed.get('outputs', {})
    reports = outputs.get('reports', {})
    plots = outputs.get('plots', {})

    styles = plots.get('styles', {})
    figures = plots.get('figures', {})

    document = {}

    data_section = load_data_section(data)

    import ipdb; ipdb.set_trace()

    return document


def test_one():
    one_path = 'tests/examples/one/sed.json'
    with open(one_path, 'r') as one_file:
        sed = json.load(one_file)

    document = transpile(sed)


if __name__ == '__main__':
    test_one()
