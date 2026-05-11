from pathlib import Path
from typing import Any
from sed.transpiler.importers.tasks import load_tasks_section, AbstractTask, ExplicitODESimulation
from sed.transpiler.importers.outputs import load_outputs_section
from pbest.utils.builder import CompositeBuilder

import pandas as pd

# from basico import load_model_from_string


class SedDocument():
    """The document itself."""
    def __init__(self, config: dict, context):
        self.versionStr = config.pop("versionStr", None)
        self.versionNum = config.pop("versionNum", None)
        self.constants = config.pop("constants", {})
        self.tasks: dict[str, AbstractTask] = load_tasks_section(config.pop("tasks", {}))
        self.outputs = load_outputs_section(config.pop("outputs", {}))
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

    def exportToPBG(self, root_dir: Path) -> dict[str, Any]:
        defaults_for_now = {}
        builder = CompositeBuilder()
        for task in self.tasks:
            task_object = self.tasks[task]
            if isinstance(task_object, ExplicitODESimulation):
                self.tasks[task].exportToPbgRepresentation(builder, self.tasks)

        return builder.get_builder_state()



    def exportToPython(self, path):
        headers = set()
        python = "# Translation of SED document v" + self.versionStr + " to python\n"
        if len(self.constants):
            python += "\n# Constants:\n"
            for constid in self.constants:
                python += "constants_" + constid + " = " + str(self.constants[constid]) + "\n"
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


