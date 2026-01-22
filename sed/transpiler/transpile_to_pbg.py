import json
import logging
import pprint
from pathlib import Path
from typing import Any

from inputs_manager import load_inputs_section
from outputs_manager import load_outputs_section
from tasks_manager import load_tasks_section

logger = logging.getLogger(__name__)

# from pbest import CompositeBuilder


# TODO: need to import the database
#   containing information about the
#   different task types and their
#   available inputs and outputs

# TODO: provide a way to validate the
#   document directly without needing to
#   actually run it (???)




def export_to_pbg(sed, context, path):
    pbg = {"data": {},
           "models": {}}

    for data_key, data_object in sed['inputs']['data'].items():
        pbg['data'][data_key] = data_object.load(path)

    for model_key, model_object in sed['inputs']['models'].items():
        pbg['models'][model_key] = model_object.load_model(path)

    for task_key, task_data in sed['tasks'].items():
        type_key = task_data.type_key

        step_name = task_data.default_step_name()
        if 'tasks' in context and task_key in context['tasks']:
            step_name = context['tasks'][task_key]

        step_config = {
            "_type": "step",
            "address": f"local:{step_name}",
            "config": {"model_source": context['root_dir'] / sed['inputs']['models']['model1'].location, "n_points": 10, "time": 1},
            "_inputs": task_data.make_inputs_schema(),
            "inputs": task_data.make_inputs(),
            "_outputs": task_data.make_outputs_schema(),
            "outputs": task_data.make_outputs(task_key)
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

def translate_to_pbg(seddoc, context, path):
    pbg = export_to_pbg(seddoc, context, path)

    return pbg    

def transpile(path, filename, context={}):
    path = Path(path)
    sed_path = path / filename

    with open(sed_path) as sed_file:
        sed = json.load(sed_file)

    seddoc = load_sed(sed, path)
    pbg = translate_to_pbg(seddoc, context, path)
    return pbg


if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parents[2]
    context = {
        'tasks': {
            'sim2': 'pbest.registry.simulators.copasi_process.CopasiUTCStep'},
        'root_dir': root_dir}

    pbg1 = transpile(root_dir / "examples/one/", "sed.json", context)
    pprint.pprint(pbg1)
    print("")

    pbg2 = transpile(root_dir / "examples/two/", "sed.json", context)
    pprint.pprint(pbg2)
    
