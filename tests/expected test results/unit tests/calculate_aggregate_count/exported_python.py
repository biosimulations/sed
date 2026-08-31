import collections
import numpy as np
import pandas as pd


# Translation of SED document vSED v2.0 alpha to python

# Constants:
constants_X = [0, 1, 0, 2, 3, 0]

# All tasks:

# Task X_count:
if isinstance(constants_X, (dict, pd.DataFrame)):
    tasks_X_count = pd.DataFrame([{k: np.count_nonzero(v, axis=0) for k, v in constants_X.items()}])
else:
    tasks_X_count = np.count_nonzero(constants_X, axis=0)

# All Outputs:

# Output report:
header = True
outputs_report = tasks_X_count
if isinstance(outputs_report, (collections.abc.Mapping, pd.DataFrame)):
   for key in outputs_report:
      outputs_report[key] = np.atleast_1d(outputs_report[key])
else:
   header = False
   outputs_report = np.atleast_1d(outputs_report)
pd.DataFrame(outputs_report).to_csv("outputs_report.csv", index=False, header=header)
