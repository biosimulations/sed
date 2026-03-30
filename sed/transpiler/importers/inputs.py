from abc import ABC, abstractmethod
from enum import EnumType
from pathlib import Path
from typing import Any

import pandas as pd
# from basico import load_model_from_string

class Model(object):
    """A 'model' object, used as input for simulators."""

    def __init__(self, model_config: dict):
        self.location = model_config.pop("location", None)
        self.language = model_config.pop("language", None)
        self.validate(model_config)
    
    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Model:", leftovers)
            return True
        return False

    def make_python(self, key, root_dir):
        headers = set()
        code = "inputs_models_" + key + " = r'" + str(Path(root_dir) / self.location) + "'\n"
        return headers, code

    # No processing, pass the file location to appropiate step/process
    # For each reference to model in question, replace with file location
    # (In reference to specific task in question, and its config)
    # (ex. UTCCopais config: model_path=[said model])
    def load_model(self, root_dir):
        #TODO: error handling
        path = root_dir / self.location
        language = self.language
        model = {"filepath": path,
                 "language": language}
        return model


class Data(object):
    """A 'plot' object, used to define a 2D visual representation of data."""

    def __init__(self, data_config: dict):
        self.location = data_config.pop("location", None)
        self.format = data_config.pop("format", None)
        self.parameters = data_config.pop("parameters", None)
        self.validate(data_config)
        self.MEDIA_TYPES = {"http://purl.org/NET/mediatypes/text/csv": self.load_csv}
    
    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Data:", leftovers)
            return True
        return False
    
    def load(self, root):
        return self.MEDIA_TYPES[self.format](root)

    def load_csv(self, root):
        # TODO: deal with parameters (!)
        df = pd.read_csv(root / self.location)
        return {key: list(series) for key, series in df.items()}
    
    def make_python(self, key, root_dir):
        if (self.format == "http://purl.org/NET/mediatypes/text/csv"):
            headers = set(["import pandas as pd"])
            code = "inputs_data_" + key + " = pd.read_csv(r'" + str(Path(root_dir) / self.location) + "')\n"
            return headers, code
        else:
            raise ValueError("Unable to translate reading data in format '" + self.format + "'.")


    def load_data(self, root):
        # TODO: deal with all error handling (!)
    
        load_file = self.MEDIA_TYPES[self.format]
        path = root / self.location
        data = load_file(path, self.parameters)
    
        return data





def load_inputs_section(input_section: dict[Any, Any], root: Path):
    inputs = {}
    inputs["data"] = {}
    inputs["models"] = {}
    for key, config in input_section.pop("data", {}).items():
        # loaded = load_data(config, root)
        inputs["data"][key] = Data(config)

    for key, config in input_section.pop("models", {}).items():
        # loaded = load_model(config, root)
        inputs["models"][key] = Model(config)

    return inputs


