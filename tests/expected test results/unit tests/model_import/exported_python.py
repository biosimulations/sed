import numpy as np
import pandas as pd
import tellurium as te


# Translation of SED document vSED v2.0 alpha to python

# All tasks:

# Task model1:
tasks_model1_model = te.loadSBMLModel(r'C:\Users\Lucian\Desktop\sed\tests\unit test files\three_species_chain.xml')

# All Outputs:

# Output init_species_values:
outputs_init_species_values = {}
outputs_init_species_values['model1_S1'] = np.atleast_1d(tasks_model1_model['S1'])
outputs_init_species_values['model1_S2'] = np.atleast_1d(tasks_model1_model['S2'])
outputs_init_species_values['model1_S3'] = np.atleast_1d(tasks_model1_model['S3'])
pd.DataFrame(outputs_init_species_values).to_csv("outputs_init_species_values.csv", index=False)
