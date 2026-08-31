import collections
import numpy as np
import pandas as pd


# Translation of SED document vSED v2.0 alpha to python

# Constants:
constants_X = [1, 2, float('nan'), 4, float('nan')]

# All tasks:

# Task X_nanlength:
if isinstance(constants_X, (dict, pd.DataFrame)):
    tasks_X_nanlength = pd.DataFrame([{k: np.sum(~np.isnan(np.asarray(v)), axis=0) for k, v in constants_X.items()}])
else:
    tasks_X_nanlength = np.sum(~np.isnan(np.asarray(constants_X)), axis=0)

# All Outputs:

# Output report:
header = True
outputs_report = tasks_X_nanlength
if isinstance(outputs_report, (collections.abc.Mapping, pd.DataFrame)):
   for key in outputs_report:
      outputs_report[key] = np.atleast_1d(outputs_report[key])
else:
   header = False
   outputs_report = np.atleast_1d(outputs_report)
pd.DataFrame(outputs_report).to_csv("outputs_report.csv", index=False, header=header)
