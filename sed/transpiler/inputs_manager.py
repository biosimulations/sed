from abc import ABC, abstractmethod
from enum import EnumType
from pathlib import Path
from typing import Any

import pandas as pd
from basico import load_model_from_string


def load_csv(location: str, parameters: dict):
    # TODO: deal with parameters (!)
    df = pd.read_csv(location)
    return {key: list(series) for key, series in df.items()}

MEDIA_TYPES = {"http://purl.org/NET/mediatypes/text/csv": load_csv}

def load_data(data_config, root):
    # TODO: deal with all error handling (!)

    location = data_config["location"]
    data_format = data_config["format"]
    parameters = data_config.get("parameters")
    load_file = MEDIA_TYPES[data_format]
    path = root / location
    data = load_file(path, parameters)

    return data

# No processing, pass the file location to appropiate step/process
# For each reference to model in question, replace with file location
# (In reference to specific task in question, and its config)
# (ex. UTCCopais config: model_path=[said model])
def load_model():
    pass


def load_inputs_section(input_section: dict[Any, Any], root: Path):
    data = {}
    for key, config in input_section["data"].items():
        loaded = load_data(config, root)
        data[key] = loaded

    for key, config in input_section["models"].items():
        loaded = load_model()
        data[key] = loaded

    return data


