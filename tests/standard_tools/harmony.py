import os

from bsedic.pbif.tools.builder import CompositeBuilder


def test_comparison_example(fully_registered_builder: CompositeBuilder):
    model_path = f"{os.getcwd()}/tests/resources/BIOMD0000000012_url.xml"
    fully_registered_builder.add_step(address="local:biocompose.processes.tellurium_process.TelluriumUTCStep",
                                      config={"model_source": model_path,"time": 10,"n_points": 10,},
                                      inputs={"concentrations": ["species_concentrations"], "counts": ["species_counts"]},
                                      outputs={"result": ["results", "tellurium"]})
    fully_registered_builder.add_step(address="local:biocompose.processes.copasi_process.CopasiUTCStep",
                                      config={"model_source": model_path,"time": 10,"n_points": 10,},
                                      inputs={"concentrations": ["species_concentrations"], "counts": ["species_counts"]},
                                      outputs={"result": ["results", "copasi"]})
    fully_registered_builder.add_comparison_step("copasi_tellurium",
                                                 ["results"])

    compare_composite = fully_registered_builder.build()
    for key in compare_composite.state['comparison_results']['comparison_step_2']:
        pass