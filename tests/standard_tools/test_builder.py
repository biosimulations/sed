import os
import random

from process_bigraph import Composite, generate_core

from bsedic.pbif.tools.builder import CompositeBuilder


def test_parameter_scan_composite_generation():
    core = generate_core()
    builder = CompositeBuilder(core=core)
    step_name = "biocompose.processes.tellurium_process.TelluriumUTCStep"
    times = [1, 10, 100]
    px = [0, 1, 2]
    py = [3, 4, 5]
    pz = [6, 7, 8]
    builder.add_parameter_scan(
        step_name=step_name,
        step_config={
            "model_source": "any_path",
            "time": 10,
            "n_points": 10,
        },
        config_values={"time": times},
        state_values={
            "species_concentrations": {"PX": px, "PY": py, "PZ": pz},
        },
        input_mappings={"concentrations": ["species_concentrations"], "counts": ["species_counts"]},
    )
    unique_input = set()
    combination_len = 3 * 3 * 3 * 3
    keys_of_interest = [k for k in builder.state["parameter_scan_0"] if "TelluriumUTCStep" in k]
    assert len(keys_of_interest) == combination_len

    # Take generated composite, and ensure every combination is unique
    for k in keys_of_interest:
        param_inputs = builder.state["parameter_scan_0"]["inputs"]
        param_config = builder.state["parameter_scan_0"][k]["config"]
        values_in_step = (
            f"PX{param_inputs[k]['species_concentrations']['PX']}:"
            f"PY{param_inputs[k]['species_concentrations']['PY']}:"
            f"PZ{param_inputs[k]['species_concentrations']['PZ']}:"
            f"Time{param_config['time']}"
        )
        assert values_in_step not in unique_input
        unique_input.add(values_in_step)
    assert len(unique_input) == combination_len

    # Ensure expected combination is in set
    assert "PX2:PY3:PZ8:Time1" in unique_input
    for _k in range(10):
        assert (
            f"PX{random.sample(px, k=1)[0]}:"
            f"PY{random.sample(py, k=1)[0]}:"
            f"PZ{random.sample(pz, k=1)[0]}:"
            f"Time{random.sample(times, k=1)[0]}" in unique_input
        )


def test_parameter_scan():
    core = generate_core()
    builder = CompositeBuilder(core=core)
    model_path = f"{os.getcwd()}/tests/resources/BIOMD0000000012_url.xml"
    px = [0, 1]
    py = [3]
    pz = [7, 9, 10]
    times = [1, 10]
    builder.add_parameter_scan(
        step_name="biocompose.processes.tellurium_process.TelluriumUTCStep",
        step_config={
            "model_source": model_path,
            "time": 10,
            "n_points": 10,
        },
        config_values={"time": times},
        state_values={
            "species_concentrations": {"PX": px, "PY": py, "PZ": pz},
        },
        input_mappings={"concentrations": ["species_concentrations"], "counts": ["species_counts"]},
    )
    param_composite = builder.build()
    param_state = param_composite.state["parameter_scan_0"]
    step_name = "biocompose.processes.tellurium_process.TelluriumUTCStep"
    result_set = [
        {"results": param_state["results"][k], "step": param_state[k], "inputs": param_state["inputs"][k]}
        for k in param_state
        if "TelluriumUTCStep" in k
    ]
    for px_i in px:
        for py_i in py:
            for pz_i in pz:
                for time_i in times:
                    state = {
                        "species_concentrations": {"PX": px_i, "PY": py_i, "PZ": pz_i},
                        "species_counts": {},
                        "tellurium_step": {
                            "_type": "step",
                            "address": f"local:{step_name}",
                            "config": {
                                "model_source": model_path,
                                "time": time_i,
                                "n_points": 10,
                            },
                            "inputs": {"concentrations": ["species_concentrations"], "counts": ["species_counts"]},
                            "outputs": {
                                "result": ["results", "tellurium"],
                            },
                        },
                    }
                    cur_comp = Composite(config={"state": state}, core=core)
                    res = cur_comp.state["results"]["tellurium"]

                    # Ensure there is still something to check
                    assert len(result_set) > 0

                    for param in result_set:
                        check = (
                            param["inputs"]["species_concentrations"]["PX"] == px_i
                            and param["inputs"]["species_concentrations"]["PY"] == py_i
                            and param["inputs"]["species_concentrations"]["PZ"] == pz_i
                            and param["step"]["config"]["time"] == time_i
                        )
                        if check:
                            assert res == param["results"]
                            result_set.remove(param)

    # Checked every combination
    assert len(result_set) == 0
