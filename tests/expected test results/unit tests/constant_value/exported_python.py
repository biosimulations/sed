import numpy as np
import pandas as pd


# Translation of SED document vSED v2.0 alpha to python

# Constants:
constants_X = 5

# All tasks:

# All Outputs:

# Output report:
outputs_report = {}
outputs_report['X'] = np.atleast_1d(constants_X)
pd.DataFrame(outputs_report).to_csv("outputs_report.csv", index=False)
