from pandas import DataFrame
import basico
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tellurium as te


# Translation of SED document vSED v2.0 alpha to python

# All tasks:

# Task model1:
inputs_models_model1 = r'C:\Users\Lucian\Desktop\sed\examples\one\example1.xml'

# Task experiment1:
inputs_data_experiment1 = pd.read_csv(r'C:\Users\Lucian\Desktop\sed\examples\one\experimental_data.csv')

# Task sim1:
tasks_sim1_r = te.loadSBMLModel(inputs_models_model1)
tasks_sim1 = tasks_sim1_r.simulate(0, 20, steps=50, selections = ['time', 'S1', 'S2'])
tasks_sim1 = pd.DataFrame(tasks_sim1, columns=tasks_sim1.colnames)

# Task sim2:
tasks_sim2_copasi = basico.run_time_course(start_time=0, duration=20, intervals=50, update_model=True, use_sbml_id=True,model=basico.load_model(inputs_models_model1))
tasks_sim2 = {}
tasks_sim2['S1'] = np.array(tasks_sim2_copasi['S1'])
tasks_sim2['S2'] = np.array(tasks_sim2_copasi['S2'])
tasks_sim2 = DataFrame(tasks_sim2)

# Task sim1_sim2_compare:
tasks_sim1_sim2_compare = (tasks_sim1 - tasks_sim2)**2

# Task sim1_exp_compare:
tasks_sim1_exp_compare = (tasks_sim1 - inputs_data_experiment1)**2

# Task sim2_exp_compare:
tasks_sim2_exp_compare = (tasks_sim2 - inputs_data_experiment1)**2

# Task compare_summary:
tasks_compare_summary = [sum(tasks_sim1_sim2_compare['S1']) + sum(tasks_sim1_sim2_compare['S2']), sum(tasks_sim1_exp_compare['S1']) + sum(tasks_sim1_exp_compare['S2']), sum(tasks_sim2_exp_compare['S1']) + sum(tasks_sim2_exp_compare['S2'])]

# Task simcompare_v2:

# All Outputs:

# Output sim1Report:
outputs_sim1Report = tasks_sim1

# Output sim2Report:
outputs_sim2Report = tasks_sim2

# Output comparisonReport:
outputs_comparisonReport = {}
outputs_comparisonReport['time'] = np.atleast_1d(tasks_sim1['time'])
pd.DataFrame(outputs_comparisonReport).to_csv("outputs_comparisonReport.csv", index=False)
outputs_comparisonReport['S1_ssq_sim1sim2'] = np.atleast_1d(tasks_sim1_sim2_compare['S1'])
pd.DataFrame(outputs_comparisonReport).to_csv("outputs_comparisonReport.csv", index=False)
outputs_comparisonReport['S1_ssq_sim1exp'] = np.atleast_1d(tasks_sim1_exp_compare['S1'])
pd.DataFrame(outputs_comparisonReport).to_csv("outputs_comparisonReport.csv", index=False)
outputs_comparisonReport['S1_ssq_sim2exp'] = np.atleast_1d(tasks_sim2_exp_compare['S1'])
pd.DataFrame(outputs_comparisonReport).to_csv("outputs_comparisonReport.csv", index=False)
outputs_comparisonReport['S2_ssq_sim1sim2'] = np.atleast_1d(tasks_sim1_sim2_compare['S2'])
pd.DataFrame(outputs_comparisonReport).to_csv("outputs_comparisonReport.csv", index=False)
outputs_comparisonReport['S2_ssq_sim1exp'] = np.atleast_1d(tasks_sim1_exp_compare['S2'])
pd.DataFrame(outputs_comparisonReport).to_csv("outputs_comparisonReport.csv", index=False)
outputs_comparisonReport['S2_ssq_sim2exp'] = np.atleast_1d(tasks_sim2_exp_compare['S2'])
pd.DataFrame(outputs_comparisonReport).to_csv("outputs_comparisonReport.csv", index=False)

# Output comparisonSummary:
outputs_comparisonSummary = tasks_compare_summary

# Output Fig1:
fig, ax = plt.subplots()
ys = np.vstack((tasks_sim1['S1'], tasks_sim1['S2'], tasks_sim2['S1'], tasks_sim2['S2'], inputs_data_experiment1['S1'], inputs_data_experiment1['S2'], ))
ys = ys.transpose()
x = tasks_sim1['time']
ax.plot(x, ys)
ax.set(xlabel='Time', ylabel='Concentrations', title='Figure 1')
plt.savefig('Fig1.png')
plt.show()
