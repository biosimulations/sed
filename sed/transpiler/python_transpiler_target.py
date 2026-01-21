import json
import sys
from pathlib import Path

import pbest.globals
from pandas import DataFrame
from process_bigraph import Composite
from roadrunner import RoadRunner
import tellurium as te
import pandas as pd
import numpy as np
import math

from basico import (
    get_reactions,
    get_species,
    load_model,
    run_steadystate,
    run_time_course,
)


PROJECT_ROOT_DIR = Path(__file__).resolve().parents[2]

def transpiler_target(demo_number: int):
    match demo_number:
        case 1:
            print("=== Performing Comparison Experiment ===")
            example_one_dir = PROJECT_ROOT_DIR / "examples" / "one"
            with open(example_one_dir / "sed.json") as f:
                print(f"Sed Document:\n {f.read()}")
            rr: RoadRunner = te.loadSBMLModel(str(example_one_dir / "example1.xml"))
            tellurium_result = rr.simulate(0, 20, 51, selections=["time", "S1", "S2"])

            copasi_df: DataFrame = run_time_course(
                start_time=0,
                duration=20,
                intervals=50,
                update_model=True,
                use_sbml_id=True,
                model=load_model(str(example_one_dir / "example1.xml"))
            )
            copasi_out = {}
            copasi_out["time"] = np.array(copasi_df.index)
            copasi_out["S1"] = np.array(copasi_df["S1"])
            copasi_out["S2"] = np.array(copasi_df["S2"])
            copasi_out = DataFrame(copasi_out)

            csv_df: DataFrame = pd.read_csv(example_one_dir / "experimental_data.csv")
            print(csv_df)
            print(copasi_df)
            print(tellurium_result)
            
            copasi_exp_diff = (copasi_out - csv_df)**2
            tellurium_exp_diff = (tellurium_result - csv_df)**2
            copasi_tell_diff = (copasi_out - tellurium_result)**2
            ce_sum = 0
            te_sum = 0
            ct_sum = 0
            for key in ["time", "S1", "S2"]:
                ce_sum += sum(copasi_exp_diff[key])
                te_sum += sum(tellurium_exp_diff[key])
                ct_sum += sum(copasi_tell_diff[key])
                
            print(ct_sum, ce_sum, te_sum)
            


        case 2:
            pass
        case 3:
            pass
        case _:
            raise RuntimeError(f"An invalid demo number was given: {demo_number}.")



if __name__ == "__main__":
    transpiler_target(1)


