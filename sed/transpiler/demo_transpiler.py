import json
import sys
from pathlib import Path

import pbest.globals
from pandas import DataFrame
from process_bigraph import Composite
from roadrunner import RoadRunner
import tellurium as te
import pandas as pd

from basico import (
    get_reactions,
    get_species,
    load_model,
    run_steadystate,
    run_time_course,
)


PROJECT_ROOT_DIR = Path(__file__).resolve().parents[2]

def demo_transpiler(demo_number: int):
    match demo_number:
        case 1:
            print("=== Performing Comparison Experiment ===")
            example_one_dir = PROJECT_ROOT_DIR / "examples" / "one"
            with open(example_one_dir / "sed.json") as f:
                print(f"Sed Document:\n {f.read()}")
            rr: RoadRunner = te.loadSBMLModel(str(example_one_dir / "example1.xml"))
            tellurium_result = rr.simulate(0, 20, 50, selections=["time", "S1", "S2"])

            copasi_df: DataFrame = run_time_course(
                start_time=0,
                duration=20,
                intervals=50,
                update_model=True,
                use_sbml_id=True,
                model=load_model(str(example_one_dir / "example1.xml"))
            )

            csv_df: DataFrame = pd.read_csv(example_one_dir / "experimental_data.csv")
            print(copasi_df)
            print(tellurium_result)
            print(csv_df)


        case 2:
            pass
        case 3:
            pass
        case _:
            raise RuntimeError(f"An invalid demo number was given: {demo_number}.")



if __name__ == "__main__":
    core = pbest.globals.get_loaded_core()
    with open(PROJECT_ROOT_DIR / "examples" / "one" / "example.pbg") as f:
        pbg = json.load(f)
        composite = Composite(core=core, config={"state": pbg})
        print(composite.state["comparison_result"])
        composite.run(1)


