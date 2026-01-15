import json
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from inputs_manager import load_inputs_section
from outputs_manager import load_outputs_section
from tasks_manager import load_tasks_section


# TODO: need to import the database
#   containing information about the
#   different task types and their
#   available inputs and outputs

# TODO: provide a way to validate the
#   document directly without needing to
#   actually run it (???)


def make_outputs(type_key, outputs):
    if type_key == "uniformTimeCourse":
        return dict.fromkeys(outputs, "array[float]")


def parse_hash(var_hash):
    return var_hash[1:].split(":")


def make_inputs(type_key, inputs):
    result = {}
    if type_key == "uniformTimeCourse":
        for key, pb_input in inputs.items():
            if isinstance(pb_input, str) and pb_input.startswith("#"):
                result[key] = parse_hash(pb_input)
            else:
                result[key] = [key]

    return result


def transpile(sed: dict[Any, Any], root_dir=None) -> dict[str, Any]:
    root_dir = Path(root_dir or ".")

    inputs = sed.get("inputs", {})
    tasks = sed.get("tasks", {})
    outputs = sed.get("outputs", {})

    document = {}

    data_section = load_inputs_section(inputs, root_dir)
    document.update(data_section)

    tasks_section = load_tasks_section(tasks)
    document.update(tasks_section)

    output_section = load_outputs_section(outputs)
    document.update(output_section)


    # ipdb.set_trace()

    return document


def load_sed(path, filename):
    path = Path(path)
    sed_path = path / filename

    with open(sed_path) as sed_file:
        sed = json.load(sed_file)

    document = transpile(sed, path)

    return document



if __name__ == "__main__":
    document = load_sed("../../examples/one/", "sed.json")
    print(document)
    print("\n\n\n")

    document = load_sed("../../examples/two/", "sed.json")
    print(document)
