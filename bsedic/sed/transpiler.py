import csv
import json
import numpy as np
import pandas as pd
from pathlib import Path

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
    return {
        key: np.array(series)
        for key, series in df.items()}


MEDIA_TYPES = {
    "http://purl.org/NET/mediatypes/text/csv": load_csv}


def load_data(data_config, root):
    # TODO: deal with all error handling (!)

    location = data_config['location']
    format = data_config['format']
    parameters = data_config.get('parameters')
    load_file = MEDIA_TYPES[format]
    path = root / location
    data = load_file(path, parameters)

    return data


def load_data_section(data_section_config, root):
    data = {}
    for key, config in data_section_config.items():
        loaded = load_data(config, root)
        data[key] = loaded

    return data


def make_outputs(type_key, outputs):
    if type_key == 'uniformTimeCourse':
        return {
            key: 'array[float]'
            for key in outputs}


def parse_hash(hash):
    return hash[1:].split(':')

def make_inputs(type_key, inputs):
    result = {}
    if type_key == 'uniformTimeCourse':
        for key, input in inputs.items():
            if isinstance(input, str) and input.startswith('#'):
                result[key] = parse_hash(input)
            else:
                result[key] = [key]

    return result


def load_tasks_section(tasks_section_config, root):
    tasks = {}
    for key, config in tasks_section_config.items():
        step_type = config.pop('_type')
        if 'outputVariables' in config:
            outputs = config.pop('outputVariables')
        else:
            outputs = [f'{key}_result']

        step_config = {
            '_type': 'step',
            'address': f'local:{step_type}',
            'config': {},
            'inputs': make_inputs(
                step_type,
                config),
            '_outputs': make_outputs(
                step_type,
                outputs),
            'outputs': {
                output_key: [key, output_key]
                for output_key in outputs}}

        tasks[key] = step_config

    return tasks


def transpile(sed, root=None):
    root = Path(root or '.')

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

    data_section = load_data_section(data, root)
    document.update(data_section)

    tasks_section = load_tasks_section(tasks, root)
    document.update(tasks_section)

    import ipdb; ipdb.set_trace()

    return document


CANONICAL_SED_NAME = 'sed.json'


def load_sed(path):
    path = Path(path)
    sed_path = path / CANONICAL_SED_NAME

    with open(sed_path, 'r') as sed_file:
        sed = json.load(sed_file)

    document = transpile(sed, path)

    return document


def test_one():
    document = load_sed('tests/examples/one/')
    
    import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    test_one()
