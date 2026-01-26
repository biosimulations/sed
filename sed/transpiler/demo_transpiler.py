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
import matplotlib.pyplot as plt

from basico import (
    get_reactions,
    get_species,
    load_model,
    run_steadystate,
    run_time_course,
)


PROJECT_ROOT_DIR = Path(__file__).resolve().parents[2]


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
            print(copasi_exp_diff, tellurium_exp_diff, copasi_tell_diff)

