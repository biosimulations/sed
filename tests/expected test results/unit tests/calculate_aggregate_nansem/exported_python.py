from scipy.stats import sem
import collections
import numpy as np
import pandas as pd


# Translation of SED document vSED v2.0 alpha to python

# Constants:
constants_X = [1, 2, float('nan'), 4.7, -5.8]

# All tasks:

# Task X_nansem:
if isinstance(constants_X, (dict, pd.DataFrame)):
    tasks_X_nansem = pd.DataFrame([{k: sem(v, axis=0, nan_policy='omit') for k, v in constants_X.items()}])
else:
    tasks_X_nansem = sem(constants_X, axis=0, nan_policy='omit')

# All Outputs:

# Output report:
header = True
outputs_report = tasks_X_nansem
if isinstance(outputs_report, (collections.abc.Mapping, pd.DataFrame)):
   for key in outputs_report:
      outputs_report[key] = np.atleast_1d(outputs_report[key])
else:
   header = False
   outputs_report = np.atleast_1d(outputs_report)
pd.DataFrame(outputs_report).to_csv("outputs_report.csv", index=False, header=header)
