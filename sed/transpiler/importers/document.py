from pathlib import Path
from typing import Any
from sed.transpiler.importers.tasks import load_tasks_section, AbstractTask
from sed.transpiler.importers.outputs import load_outputs_section
from sed.transpiler.library import python_literal, interpret_special_strings
from pbest.utils.builder import CompositeBuilder

import pandas as pd

# from basico import load_model_from_string


class SedDocument():
    """The document itself."""
    def __init__(self, config: dict, context):
        config = interpret_special_strings(config)
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
            self.tasks[task].exportToPBG()


    def exportToPython(self, path):
        headers = set()
        python = f"# Translation of SED document v{self.versionStr} to python\n"
        if len(self.constants):
            python += "\n# Constants:\n"
            for constid in self.constants:
                python += f"constants_{constid} = {python_literal(self.constants[constid])}\n"
        python +=  "\n# All tasks:\n"
        for taskid in self.tasks:
            python +=  f"\n# Task {taskid}:\n"
            newheaders, newpython = self.tasks[taskid].exportToPython(f"#tasks:{taskid}", path)
            headers.update(newheaders)
            python += newpython
        python +=  "\n# All Outputs:\n"
        for output in self.outputs:
            python +=  f"\n# Output {output}:\n"
            newheaders, newpython = self.outputs[output].exportToPython(output, path)
            headers.update(newheaders)
            python += newpython
        return headers, python
