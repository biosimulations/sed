import json
import logging
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


def export_to_python(sed, context, path):
    headers = set()
    python = ""
    if 'data' in sed['inputs']:
        for data_key, data_object in sed['inputs']['data'].items():
            h, p = data_object.make_python(data_key, path)
            headers.update(h)
            python += "\n# inputs:data:" + data_key + "\n"
            python += p

    if 'models' in sed['inputs']:
        for model_key, model_object in sed['inputs']['models'].items():
            h, p = model_object.make_python(model_key, path)
            headers.update(h)
            python += "\n# inputs:models:" + model_key + "\n"
            python += p

    for task_key, task_object in sed['tasks'].items():
        if "tasks" in context and task_key in context['tasks']:
            task_object.executor = context['tasks'][task_key]
        h, p = task_object.make_python(task_key)
        headers.update(h)
        python += "\n# tasks:" + task_key + "\n"
        python += p

    if 'reports' in sed['outputs']:
        for report_key, report_object in sed['outputs']['reports'].items():
            h, p = report_object.make_python(report_key)
            headers.update(h)
            python += "\n# reports:" + report_key + "\n"
            python += p

    if 'plots' in sed['outputs']:
        for plot_key, plot_object in sed['outputs']['plots'].items():
            h, p = plot_object.make_python(plot_key)
            headers.update(h)
            python += "\n# plots:" + plot_key + "\n"
            python += p

    return headers, python
    

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

def translate_to_python(seddoc, context, path):

    headers, python = export_to_python(seddoc, context, path)

    ret = ""
    for header in headers:
        ret += header + "\n"
    ret += "\n\n" + python

    return ret


def transpile(path, filename, context={}):
    path = Path(path)
    sed_path = path / filename

    with open(sed_path) as sed_file:
        sed = json.load(sed_file)

    seddoc = load_sed(sed, path)
    print(seddoc)
    python = translate_to_python(seddoc, context, path)
    return python


if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parents[2]
    context = {
        'tasks': {
            'sim2': 'Copasi'}}
    python1 = transpile(root_dir / "examples/one/", "sed.json", context)
    print("")
    print(python1)
    print("")

    python2 = transpile(root_dir / "examples/two/", "sed.json")
    print("")
    print(python2)
    
