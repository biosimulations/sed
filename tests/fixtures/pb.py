import os

import pytest
from biocompose.processes import CopasiUTCStep, TelluriumUTCStep
from process_bigraph import Composite, ProcessTypes

# from biocompose import standard_types
from bsedic.pbif.tools import standard_types
from bsedic.pbif.tools.comparison import MSEComparison


@pytest.fixture(scope="function", autouse=True)
def comparison_composite() -> Composite:
    core = ProcessTypes()

    core.register_process("TelluriumUTCStep", TelluriumUTCStep)
    core.register_process("CopasiUTCStep", CopasiUTCStep)
    core.register_process("CompareResults", MSEComparison)

    for k, i in standard_types.items():
        core.register(k, i)

    model_path = f"{os.getcwd()}/tests/resources/BIOMD0000000012_url.xml"

    state = {
        # provide initial values to overwrite those in the configured model
        "species_concentrations": {},
        "species_counts": {},
        "tellurium_step": {
            "_type": "step",
            "address": "local:TelluriumUTCStep",
            "config": {
                "model_source": model_path,
                "time": 10,
                "n_points": 10,
            },
            "inputs": {"concentrations": ["species_concentrations"], "counts": ["species_counts"]},
            "outputs": {
                "result": ["results", "tellurium"],
            },
        },
        "copasi_step": {
            "_type": "step",
            "address": "local:CopasiUTCStep",
            "config": {
                "model_source": model_path,
                "time": 10,
                "n_points": 10,
            },
            "inputs": {"concentrations": ["species_concentrations"], "counts": ["species_counts"]},
            "outputs": {
                "result": ["results", "copasi"],
            },
        },
        "comparison": {
            "_type": "step",
            "address": "local:CompareResults",
            "config": {},
            "inputs": {
                "results": ["results"],
            },
            "outputs": {
                "comparison": ["comparison_result"],
            },
        },
    }

    bridge = {"outputs": {"result": ["comparison_result"]}}

    document = {"state": state, "bridge": bridge}
    comp = Composite(document, core=core)
    return comp
