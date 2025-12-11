import os
from typing import Any

import pytest
from biocompose.processes import CopasiUTCStep, TelluriumUTCStep
from process_bigraph import Composite, ProcessTypes, generate_core

# from biocompose import standard_types
from bsedic.pbif.tools import standard_types
from bsedic.pbif.tools.builder import CompositeBuilder
from bsedic.pbif.tools.comparison import MSEComparison


@pytest.fixture(scope="function")
def fully_registered_core() -> ProcessTypes:
    core = generate_core()
    for k, i in standard_types.items():
        core.register(k, i)
    return core



@pytest.fixture(scope="function")
def fully_registered_builder(fully_registered_core) -> CompositeBuilder:
    return CompositeBuilder(core=fully_registered_core)


@pytest.fixture(scope="function", autouse=True)
def comparison_document() -> dict[Any, Any]:
    model_path = f"{os.getcwd()}/tests/resources/BIOMD0000000012_url.xml"

    state = {
        # provide initial values to overwrite those in the configured model
        "species_concentrations": {},
        "species_counts": {},
        "tellurium_step": {
            "_type": "step",
            "address": "local:biocompose.processes.tellurium_process.TelluriumUTCStep",
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
            "address": "local:biocompose.processes.copasi_process.CopasiUTCStep",
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
            "address": "local:bsedic.pbif.tools.comparison.MSEComparison",
            "config": {},
            "inputs": {
                "results": ["results"],
            },
            "outputs": {
                "comparison_result": ["comparison_result"],
            },
        },
    }

    bridge = {"outputs": {"result": ["comparison_result"]}}

    document = {"state": state, "bridge": bridge}
    return document
