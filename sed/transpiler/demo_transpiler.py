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


if __name__ == "__main__":
    core = pbest.globals.get_loaded_core()
    with open(PROJECT_ROOT_DIR / "examples" / "one" / "example.pbg") as f:
        pbg = json.load(f)
        composite = Composite(core=core, config={"state": pbg})
        print(composite.state["comparison_result"])
        composite.run(1)


