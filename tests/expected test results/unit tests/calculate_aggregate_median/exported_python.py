import collections
import numpy as np
import pandas as pd


# Translation of SED document vSED v2.0 alpha to python

# Constants:
constants_X = [1, 2, 3, 3, 5, 6, 7]

# All tasks:

# Task X_median:
if isinstance(constants_X, (dict, pd.DataFrame)):
    tasks_X_median = pd.DataFrame([{k: np.median(v, axis=0) for k, v in constants_X.items()}])
else:
    tasks_X_median = np.median(constants_X, axis=0)

# All Outputs:

# Output report:
header = True
outputs_report = tasks_X_median
if isinstance(outputs_report, (collections.abc.Mapping, pd.DataFrame)):
   for key in outputs_report:
      outputs_report[key] = np.atleast_1d(outputs_report[key])
else:
   header = False
   outputs_report = np.atleast_1d(outputs_report)
pd.DataFrame(outputs_report).to_csv("outputs_report.csv", index=False, header=header)
