from pathlib import Path
from typing import Any
from sed.transpiler.importers.tasks import load_tasks_section
from sed.transpiler.importers.outputs import load_outputs_section

import pandas as pd

# from basico import load_model_from_string


class SedDocument():
    """The document itself."""
    def __init__(self, config: dict):
        self.versionStr = config.pop("versionStr", None)
        self.versionNum = config.pop("versionNum", None)
        self.constants = config.pop("constants", None)
        self.tasks = load_tasks_section(config.pop("tasks", None))
        self.outputs = load_outputs_section(config.pop("outputs", None))
        # TODO: actually load styles.
        self.styles = config.pop("style", None)
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


