import collections
import numpy as np
import pandas as pd
import tellurium as te


# Translation of SED document vSED v2.0 alpha to python

# All tasks:

# Task model1:
tasks_model1_model = te.loadSBMLModel(r'C:\Users\Lucian\Desktop\sed\tests\unit test files\three_species_chain_stochlevels.xml')

# Task sim1:
tasks_sim1_model = te.loadSBMLModel(tasks_model1_model.getCurrentSBML())
tasks_sim1_model.setIntegrator('gillespie')
tasks_sim1 = tasks_sim1_model.simulate(0, 20, steps=100, selections = ['time', 'S1', 'S2', 'S3'])
tasks_sim1 = pd.DataFrame(tasks_sim1, columns=tasks_sim1.colnames)

# All Outputs:

# Output sim1_out:
header = True
outputs_sim1_out = tasks_sim1
if isinstance(outputs_sim1_out, (collections.abc.Mapping, pd.DataFrame)):
   for key in outputs_sim1_out:
      outputs_sim1_out[key] = np.atleast_1d(outputs_sim1_out[key])
else:
   header = False
pd.DataFrame(outputs_sim1_out).to_csv("outputs_sim1_out.csv", index=False, header=header)
