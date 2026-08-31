import collections
import numpy as np
import pandas as pd


# Translation of SED document vSED v2.0 alpha to python

# Constants:
constants_X = [0, 1, float('nan'), True, 0, float('nan'), 3]

# All tasks:

# Task X_nancount:
if isinstance(constants_X, (dict, pd.DataFrame)):
    tasks_X_nancount = pd.DataFrame([{k: np.count_nonzero(~np.isnan(np.asarray(v)) & (np.asarray(v) != 0), axis=0) for k, v in constants_X.items()}])
else:
    tasks_X_nancount = np.count_nonzero(~np.isnan(np.asarray(constants_X)) & (np.asarray(constants_X) != 0), axis=0)

# All Outputs:

# Output report:
header = True
outputs_report = tasks_X_nancount
if isinstance(outputs_report, (collections.abc.Mapping, pd.DataFrame)):
   for key in outputs_report:
      outputs_report[key] = np.atleast_1d(outputs_report[key])
else:
   header = False
   outputs_report = np.atleast_1d(outputs_report)
pd.DataFrame(outputs_report).to_csv("outputs_report.csv", index=False, header=header)
