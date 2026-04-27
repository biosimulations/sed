import typing
from pathlib import Path
from typing import Any

import pandas as pd

# from basico import load_model_from_string


class SedBase:
    """A 'model' object, used as input for simulators."""

    def __init__(self, model_config: dict):
        self.name = model_config.pop("name", None)
        self.description = model_config.pop("description", None)
        self.notes = model_config.pop("notes", None)
        self.annotations = model_config.pop("annotations", None)
        self.__validate(model_config)

    def __validate(self, leftovers={}):
        """Validate."""
        #TODO: check format for children.
        return False

def from_attribute_to_list_path(attribute: str | bool | int | SedBase) -> Any:
    if type(attribute) is bool:
        return attribute
    if type(attribute) is int:
        return attribute
    # [#tasks, model1.model], [model1, model]
    return attribute.split(":")[1].split(".") if attribute[0] == "#" else attribute


class Range(SedBase):
    """A 'range' object, used to define a range in one of several ways:
    * start, end, numberOfSteps (and optional 'scale')
    * start, end, interval
    * start, numberOfSteps, interval
    * end, numberOfSteps, interval
    * values
    """

    def __init__(self, range_config: dict):
        super().__init__(range_config)
        self.type_key = "Range"
        self.start = range_config.pop("start", None)
        self.end = range_config.pop("end", None)
        self.numberOfSteps = range_config.pop("numberOfSteps", None)
        self.interval = range_config.pop("interval", None)
        self.scale = range_config.pop("scale", None)
        self.values = range_config.pop("values", None)
        self.__validate(range_config)

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Range:", leftovers)
            return True
        return False
