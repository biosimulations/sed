from pathlib import Path
from typing import Any
from sed.transpiler.importers.tasks import load_tasks_section
from sed.transpiler.importers.outputs import load_outputs_section

import pandas as pd

# from basico import load_model_from_string


class SedDocument():
    """The document itself."""
    def __init__(self, config: dict, context):
        self.versionStr = config.pop("versionStr", None)
        self.versionNum = config.pop("versionNum", None)
        self.constants = config.pop("constants", None)
        self.tasks = load_tasks_section(config.pop("tasks", None))
        self.outputs = load_outputs_section(config.pop("outputs", None))
        # TODO: actually load styles.
        self.styles = config.pop("styles", None)
        # context = {"tasks": {"sim2": "Copasi"}}
        for tag in context:
            if tag == "tasks":
                for task in context[tag]:
                    self.tasks[task].setContext(context[tag][task])
        self.__validate(config)

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating SEDDocument:", leftovers)
            return True
        return False

    def exportToPython(self, path):
        headers = set()
        python = "# Translation of SED document v" + self.versionStr + " to python\n"
        python +=  "\n# All tasks:\n"
        for task in self.tasks:
            python +=  "\n# Task " + task + ":\n"
            newheaders, newpython = self.tasks[task].exportToPython(task, path)
            headers.update(newheaders)
            python += newpython
        python +=  "\n# All Outputs:\n"
        for output in self.outputs:
            python +=  "\n# Output " + output + ":\n"
            newheaders, newpython = self.outputs[output].exportToPython(output, path)
            headers.update(newheaders)
            python += newpython
        return headers, python


