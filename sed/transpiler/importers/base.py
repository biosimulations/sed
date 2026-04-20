from pathlib import Path
from typing import Any
from tasks import load_tasks_section
from outputs import load_outputs_section

import pandas as pd

# from basico import load_model_from_string


class SedBase:
    """A 'model' object, used as input for simulators."""

    def __init__(self, model_config: dict):
        self.name = model_config.pop("name", None)
        self.description = model_config.pop("description", None)
        self.notes = model_config.pop("notes", None)
        self.annotations = model_config.pop("annotations", None)
        self.validate(model_config)

    def validate(self, leftovers={}):
        """Validate."""
        #TODO: check format for children.
        return False


class Range(SedBase):
    """A 'range' object, used to define a range in one of several ways:
    * start, end, numberOfSteps (and optional 'scale')
    * start, end, interval
    * start, numberOfSteps, interval
    * end, numberOfSteps, interval
    * values
    """

    def __init__(self, range_config: dict):
        super().__init__(self, range_config)
        self.type_key = "Range"
        self.start = range_config.pop("start", None)
        self.end = range_config.pop("end", None)
        self.numberOfSteps = range_config.pop("numberOfSteps", None)
        self.interval = range_config.pop("interval", None)
        self.scale = range_config.pop("scale", None)
        self.values = range_config.pop("values", None)
        self.validate(range_config)

    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Range:", leftovers)
            return True
        return False

class SedDocument():
    """The document itself."""
    def __init__(self, config: dict):
        self.versionStr = config.pop("versionStr", None)
        self.versionNum = config.pop("versionNum", None)
        self.constants = config.pop("constants", None)
        self.tasks = load_tasks_section(config.pop("tasks", None))
        self.outputs = load_outputs_section(config.pop("outputs", None))
        self.validate(config)

    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating SEDDocument:", leftovers)
            return True
        return False

    def exportToPython(self, context, path):
        headers = set()
		python = "# Translation of SED document v" + sed.versionStr + " to python\n\n"
        python +=  "\n# tasks:" + task_key + "\n"
        for task in self.tasks:
            newheaders, newpython = task.exportToPython()
            headers.update(newheaders)
            python += newpython
        python +=  "\n# outputs:" + task_key + "\n"
        for output in self.outputs:
            newheaders, newpython = output.exportToPython()
            headers.update(newheaders)
            python += newpython
        return headers, python


