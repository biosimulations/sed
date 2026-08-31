import collections
import numpy as np
import pandas as pd


# Translation of SED document vSED v2.0 alpha to python

# Constants:
constants_X = [1, 2, float('nan'), 4, 5]

# All tasks:

# Task X_nanstd:
if isinstance(constants_X, (dict, pd.DataFrame)):
    tasks_X_nanstd = pd.DataFrame([{k: np.nanstd(v, axis=0) for k, v in constants_X.items()}])
else:
    tasks_X_nanstd = np.nanstd(constants_X, axis=0)

# All Outputs:

# Output report:
header = True
outputs_report = tasks_X_nanstd
if isinstance(outputs_report, (collections.abc.Mapping, pd.DataFrame)):
   for key in outputs_report:
      outputs_report[key] = np.atleast_1d(outputs_report[key])
else:
   header = False
   outputs_report = np.atleast_1d(outputs_report)
pd.DataFrame(outputs_report).to_csv("outputs_report.csv", index=False, header=header)
