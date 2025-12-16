import os

from bsedic.pbif.tools.builder import CompositeBuilder


def comparison_builder(builder: CompositeBuilder) -> None:
    model_path = f"{os.getcwd()}/tests/resources/BIOMD0000000012_url.xml"
    builder.add_step(
        address="local:biocompose.processes.tellurium_process.TelluriumUTCStep",
        config={
            "model_source": model_path,
            "time": 10,
            "n_points": 10,
        },
        inputs={"concentrations": ["species_concentrations"], "counts": ["species_counts"]},
        outputs={"result": ["results", "tellurium"]},
    )
    builder.add_step(
        address="local:biocompose.processes.copasi_process.CopasiUTCStep",
        config={
            "model_source": model_path,
            "time": 10,
            "n_points": 10,
        },
        inputs={"concentrations": ["species_concentrations"], "counts": ["species_counts"]},
        outputs={"result": ["results", "copasi"]},
    )
    builder.add_comparison_step("copasi_tellurium", ["results"])


def test_comparison_example(fully_registered_builder: CompositeBuilder):
    comparison_builder(builder=fully_registered_builder)
    compare_composite = fully_registered_builder.build()
    comparisons = compare_composite.state["comparison_results"]["copasi_tellurium"]["species_mse"]
    for simulator_of_focus in comparisons:
        for key, value in comparisons[simulator_of_focus].items():
            if key == simulator_of_focus:
                assert value == 0
            else:
                assert value < 1e-6
                assert value != 0


def test_parameter_scan(fully_registered_builder: CompositeBuilder):
    model_path = f"{os.getcwd()}/tests/resources/BIOMD0000000012_url.xml"
    fully_registered_builder.add_parameter_scan(
        step_address="local:biocompose.processes.tellurium_process.TelluriumSteadyStateStep",
        step_config={"model_source": model_path},
        input_mappings={"species_concentrations": ["species_concentrations"], "counts": ["species_counts"]},
        config_values={},
        state_values={"species_concentrations": {"PX": [1, 30000], "PY": [1, 2000], "PZ": [1, 5000]}},
    )

    comp = fully_registered_builder.build()
    steady_state_values = [
        [
            240.8222635574016,
            240.8222635574016,
            240.8222635574016,
            2.408222635574016,
            2.408222635574016,
            2.408222635574016,
        ]
    ]
    jacboian_values = [
        [-0.06931471805599441, 0.0, 0.0, 6.931471805599392, 0.0, 0.0],
        [0.0, -0.06931471805599441, 0.0, 0.0, 6.931471805599392, 0.0],
        [0.0, 0.0, -0.06931471805599441, 0.0, 0.0, 6.931471805599392],
        [0.0, 0.0, -0.006502909960777793, -0.34657359027997203, 0.0, 0.0],
        [-0.006502909960777793, 0.0, 0.0, 0.0, -0.34657359027997203, 0.0],
        [0.0, -0.006502909960777793, 0.0, 0.0, 0.0, -0.34657359027997203],
    ]

    # Seems as if values don't change over parameter scan, cause for concern?
    results = comp.state["parameter_scan_0"]["results"]
    for k in results:
        assert results[k]["jacobian"]["values"] == jacboian_values
        assert results[k]["steady_state"]["values"] == steady_state_values
