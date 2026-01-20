import json
import logging
from pathlib import Path
from typing import Any

from sed.transpiler.inputs_manager import load_inputs_section
from sed.transpiler.outputs_manager import load_outputs_section
from sed.transpiler.tasks_manager import load_tasks_section


logger = logging.getLogger(__name__)

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


def export_to_pbg(sed, context):
    pbg = sed['inputs']

    for task_key, task_data in sed['tasks'].items():
        type_key = task_data.type_key
        step_name = 'Tellurium'
        if 'tasks' in context and task_key in context['tasks']:
            step_name = context['tasks'][task_key]

        step_config = {
            "_type": "step",
            "address": f"local:{step_name}",
            "config": {},
            "_inputs": make_inputs_schema(type_key, task_data),
            "inputs": make_inputs(type_key, task_data),
            "_outputs": make_outputs_schema(type_key, task_data),
            "outputs": make_outputs(type_key, task_key, task_data)
        }

        pbg[task_key] = step_config

    return pbg
    

def load_sed(sed: dict[Any, Any], root_dir=None, context={}) -> dict[str, Any]:
    root_dir = Path(root_dir or ".")

    inputs = sed.get("inputs", {})
    tasks = sed.get("tasks", {})
    outputs = sed.get("outputs", {})

    seddoc = {}

    seddoc['inputs']  = load_inputs_section(inputs, root_dir)
    seddoc['tasks']   = load_tasks_section(tasks)
    seddoc['outputs'] = load_outputs_section(outputs)

    logger.debug(seddoc)
    logger.debug("")

    return seddoc

def translate_to_pbg(seddoc, context):

    pbg = export_to_pbg(seddoc, context)

    #import ipdb; ipdb.set_trace()

    return pbg    

def transpile(path, filename, context={}):
    path = Path(path)
    sed_path = path / filename

    with open(sed_path) as sed_file:
        sed = json.load(sed_file)

    seddoc = load_sed(sed, path)
    pbg = translate_to_pbg(seddoc, context)
    return pbg


if __name__ == "__main__":
    context = {
        'tasks': {
            'sim2': 'Copasi'}}
    pbg1 = transpile("examples/one/", "sed.json", context)
    print(pbg1)
    print("")

    pbg2 = transpile("examples/two/", "sed.json")
    print(pbg2)
    
