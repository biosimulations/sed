from pathlib import Path

from sed.transpiler.transpile_to_python import transpile

expected_python_ex_1 = """
from pandas import DataFrame
import basico
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tellurium as te



# inputs:data:experiment1
inputs_data_experiment1 = pd.read_csv(r'/Users/evalencia/Documents/BioSimulators/sed/examples/one/experimental_data.csv')

# inputs:models:model1
inputs_models_model1 = r'/Users/evalencia/Documents/BioSimulators/sed/examples/one/example1.xml'

# tasks:sim1
tasks_sim1_r = te.loadSBMLModel(inputs_models_model1)
tasks_sim1 = tasks_sim1_r.simulate(0, 20, steps=50, selections = ['time', 'S1', 'S2'])

# tasks:sim2
tasks_sim2_copasi = basico.run_time_course(start_time=0, duration=20, intervals=50, update_model=True, use_sbml_id=True,model=basico.load_model(inputs_models_model1))
tasks_sim2 = {}
tasks_sim2['time'] = np.array(tasks_sim2_copasi.index)
tasks_sim2['S1'] = np.array(tasks_sim2_copasi['S1'])
tasks_sim2['S2'] = np.array(tasks_sim2_copasi['S2'])
tasks_sim2 = DataFrame(tasks_sim2)

# tasks:sim1_sim2_compare
tasks_sim1_sim2_compare = (tasks_sim1 - tasks_sim2)**2

# tasks:sim1_exp_compare
tasks_sim1_exp_compare = (tasks_sim1 - inputs_data_experiment1)**2

# tasks:sim2_exp_compare
tasks_sim2_exp_compare = (tasks_sim2 - inputs_data_experiment1)**2

# tasks:compare_summary
tasks_compare_summary = [sum(tasks_sim1_sim2_compare['S1']) + sum(tasks_sim1_sim2_compare['S2']), sum(tasks_sim1_exp_compare['S1']) + sum(tasks_sim1_exp_compare['S2']), sum(tasks_sim2_exp_compare['S1']) + sum(tasks_sim2_exp_compare['S2'])]

# tasks:simcompare_v2

# reports:sim1Report
outputs_reports_sim1Report = tasks_sim1
print(outputs_reports_sim1Report)

# reports:sim2Report
outputs_reports_sim2Report = tasks_sim2
print(outputs_reports_sim2Report)

# reports:comparisonReport
outputs_reports_comparisonReport = {}
outputs_reports_comparisonReport['time'] = np.array(tasks_sim1['time'])
outputs_reports_comparisonReport['S1_ssq_sim1sim2'] = np.array(tasks_sim1_sim2_compare['S1'])
outputs_reports_comparisonReport['S1_ssq_sim1exp'] = np.array(tasks_sim1_exp_compare['S1'])
outputs_reports_comparisonReport['S1_ssq_sim2exp'] = np.array(tasks_sim2_exp_compare['S1'])
outputs_reports_comparisonReport['S2_ssq_sim1sim2'] = np.array(tasks_sim1_sim2_compare['S2'])
outputs_reports_comparisonReport['S2_ssq_sim1exp'] = np.array(tasks_sim1_exp_compare['S2'])
outputs_reports_comparisonReport['S2_ssq_sim2exp'] = np.array(tasks_sim2_exp_compare['S2'])
print(outputs_reports_comparisonReport)

# reports:comparisonSummary
outputs_reports_comparisonSummary = tasks_compare_summary
print(outputs_reports_comparisonSummary)

# plots:Fig1
fig, ax = plt.subplots()
ys = np.vstack((tasks_sim1['S1'], tasks_sim1['S2'], tasks_sim2['S1'], tasks_sim2['S2'], inputs_data_experiment1['S1'], inputs_data_experiment1['S2'], ))
ys = ys.transpose()
x = tasks_sim1['time']
ax.plot(x, ys)
ax.set(xlabel='Time', ylabel='Concentrations', title='Figure 1')
plt.show()
""".strip()


def test_python_transpile_ex_1():
    root_dir = Path(__file__).resolve().parents[1]
    context = {"tasks": {"sim2": "Copasi"}}
    python1 = transpile(root_dir / "examples/one/", "sed.json", context)

    assert python1.strip() == expected_python_ex_1


example_str_2 = """
import numpy as np



# inputs:models:model1
inputs_models_model1 = r'/Users/evalencia/Documents/BioSimulators/sed/examples/two/example.xml'

# tasks:paramScan_k1

# tasks:paramScan_k2

# tasks:steadyStates

# reports:steadyStateReport
outputs_reports_steadyStateReport = tasks_steadyStates
print(outputs_reports_steadyStateReport)

# reports:jacobianReport
outputs_reports_jacobianReport = tasks_jacobians
print(outputs_reports_jacobianReport)

# plots:Fig1
""".strip()


def test_python_transpile_ex_2():
    root_dir = Path(__file__).resolve().parents[1]

    python2 = transpile(root_dir / "examples/two/", "sed.json")
    assert example_str_2.strip() == python2.strip()
