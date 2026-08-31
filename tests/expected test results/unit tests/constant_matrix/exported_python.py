import collections
import numpy as np
import pandas as pd


# Translation of SED document vSED v2.0 alpha to python

# Constants:
constants_X = [[0, 1, 2, 5, 10, 20, 50], [0, 1, 2, 3, 4, 5, 6], [0, -1, -1, -2, -2, -3, -3], [0, 1.209872, 2.29062, 5e+20, 0.00123465, 0.0001, 400.2456]]

# All tasks:

# All Outputs:

# Output report_labels:
outputs_report_labels = {}
outputs_report_labels['X1'] = np.atleast_1d(constants_X[0])
outputs_report_labels['X2'] = np.atleast_1d(constants_X[1])
outputs_report_labels['X3'] = np.atleast_1d(constants_X[2])
outputs_report_labels['X4'] = np.atleast_1d(constants_X[3])
pd.DataFrame(outputs_report_labels).to_csv("outputs_report_labels.csv", index=False)

# Output report_no_labels:
header = True
outputs_report_no_labels = constants_X
if isinstance(outputs_report_no_labels, (collections.abc.Mapping, pd.DataFrame)):
   for key in outputs_report_no_labels:
      outputs_report_no_labels[key] = np.atleast_1d(outputs_report_no_labels[key])
else:
   header = False
   outputs_report_no_labels = np.atleast_1d(outputs_report_no_labels)
pd.DataFrame(outputs_report_no_labels).to_csv("outputs_report_no_labels.csv", index=False, header=header)
