import numpy as np
import pandas as pd


# Translation of SED document vSED v2.0 alpha to python

# Constants:
constants_X = {'time': [0, 1, 2, 5, 10, 20, 50], 'S1': [0, 1, 2, 3, 4, 5, 6], 'k3': [0, -1, -1, -2, -2, -3, -3], 'err': [0, 1.209872, 2.29062, 5e+20, 0.00123465, 0.0001, 400.2456]}

# All tasks:

# All Outputs:

# Output report:
outputs_report = constants_X
for key in outputs_report:
   outputs_report[key] = np.atleast_1d(outputs_report[key])
pd.DataFrame(outputs_report).to_csv("outputs_report.csv", index=False)
