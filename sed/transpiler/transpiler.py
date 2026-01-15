import json
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from inputs_manager import load_inputs_section
from outputs_manager import load_outputs_section
from tasks_manager import load_tasks_section, UniformTimeCourse

# from pbest import CompositeBuilder


# TODO: need to import the database
#   containing information about the
#   different task types and their
#   available inputs and outputs

# TODO: provide a way to validate the
#   document directly without needing to
#   actually run it (???)


def make_inputs_schema(type_key, task_data):
    result = {}
    if type_key == "UniformTimeCourse":
        return {'model': 'string'}


def make_inputs(type_key, task_data):
    result = {}
    if type_key == "UniformTimeCourse":
        return {'model': parse_hash(task_data.model)}


def make_outputs_schema(type_key, task_data):
    if type_key == "UniformTimeCourse":
        outputs = {}
        for key in task_data.outputVariables:
            outputs[key] = "array[float]"
        return outputs


def make_outputs(type_key, task_key, task_data):
    if type_key == "UniformTimeCourse":
        outputs = {}
        for key in task_data.outputVariables:
            outputs[key] = ['results', task_key, key]
        return outputs


def parse_hash(var_hash):
    return var_hash[1:].split(":")[1:]


def task_to_step(task_data):
    if isinstance(task_data, UniformTimeCourse):
        return "UniformTimeCourse"


def export_to_pbg(sed, context):
    pbg = sed['inputs']

    for task_key, task_data in sed['tasks'].items():
        step_task = task_to_step(task_data)
        step_name = 'Tellurium'
        if task_key in context['tasks']:
            step_name = context['tasks'][task_key]

        step_config = {
            "_type": "step",
            "address": f"local:{step_name}",
            "config": {},
            "_inputs": make_inputs_schema(step_task, task_data),
            "inputs": make_inputs(step_task, task_data),
            "_outputs": make_outputs_schema(step_task, task_data),
            "outputs": make_outputs(step_task, task_key, task_data)
        }

        pbg[task_key] = step_config

    return pbg
    

def transpile(sed: dict[Any, Any], root_dir=None) -> dict[str, Any]:
    root_dir = Path(root_dir or ".")

    inputs = sed.get("inputs", {})
    tasks = sed.get("tasks", {})
    outputs = sed.get("outputs", {})

    document = {}

    inputs_section = load_inputs_section(inputs, root_dir)
    document['inputs'] = inputs_section

    tasks_section = load_tasks_section(tasks)
    document['tasks'] = tasks_section

    outputs_section = load_outputs_section(outputs)
    document['outputs'] = outputs_section

    context = {
        'tasks': {
            'sim2': 'Copasi'}}

    pbg = export_to_pbg(document, context)

    import ipdb; ipdb.set_trace()

    return document


def load_sed(path, filename):
    path = Path(path)
    sed_path = path / filename

    with open(sed_path) as sed_file:
        sed = json.load(sed_file)

    document = transpile(sed, path)

    return document



if __name__ == "__main__":
    document = load_sed("examples/one/", "sed.json")
    print(document)
    print("")

    document = load_sed("examples/two/", "sed.json")
    print(document)
