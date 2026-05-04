import numpy as np
import pandas as pd


# Translation of SED document vSED v2.0 alpha to python

# All tasks:

# Task data1:
tasks_data1 = pd.read_csv(r'C:\Users\Lucian\Desktop\sed\tests\unit test files\experimental_data.csv')

# All Outputs:

# Output experimental_species_values:
outputs_experimental_species_values = {}
outputs_experimental_species_values['data1_S1'] = np.atleast_1d(tasks_data1['S1'])
outputs_experimental_species_values['data1_S2'] = np.atleast_1d(tasks_data1['S2'])
outputs_experimental_species_values['data1_S3'] = np.atleast_1d(tasks_data1['S3'])
pd.DataFrame(outputs_experimental_species_values).to_csv("outputs_experimental_species_values.csv", index=False)
