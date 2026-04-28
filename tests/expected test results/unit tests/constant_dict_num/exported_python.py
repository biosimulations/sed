import numpy as np
import pandas as pd


# Translation of SED document vSED v2.0 alpha to python

# Constants:
constants_X = {'time': 50, 'S1': 6, 'k3': -3, 'err': 400.2456}

# All tasks:

# All Outputs:

# Output report:
outputs_report = constants_X
for key in outputs_report:
   outputs_report[key] = np.atleast_1d(outputs_report[key])
pd.DataFrame(outputs_report).to_csv("outputs_report.csv", index=False)
