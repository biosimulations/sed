from pathlib import Path

from sed.transpiler.transpile_to_python import transpile
import subprocess, sys, os

root_dir = Path(__file__).resolve().parents[1]
ex1 = Path(root_dir, "examples", "one", "example1.xml")
data = Path(root_dir, "examples", "one", "experimental_data.csv")

expected_python_ex_1 = """
from pandas import DataFrame
import basico
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tellurium as te


# Translation of SED document vSED v2.0 alpha to python

# All tasks:

# Task model1:
inputs_models_model1 = r'""" + str(ex1) + """'

# Task experiment1:
inputs_data_experiment1 = pd.read_csv(r'""" + str(data) + """')

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
outputs_reports_sim1Report = tasks_sim1
print(outputs_reports_sim1Report)

# Output sim2Report:
outputs_reports_sim2Report = tasks_sim2
print(outputs_reports_sim2Report)

# Output comparisonReport:
outputs_reports_comparisonReport = {}
outputs_reports_comparisonReport['time'] = np.array(tasks_sim1['time'])
outputs_reports_comparisonReport['S1_ssq_sim1sim2'] = np.array(tasks_sim1_sim2_compare['S1'])
outputs_reports_comparisonReport['S1_ssq_sim1exp'] = np.array(tasks_sim1_exp_compare['S1'])
outputs_reports_comparisonReport['S1_ssq_sim2exp'] = np.array(tasks_sim2_exp_compare['S1'])
outputs_reports_comparisonReport['S2_ssq_sim1sim2'] = np.array(tasks_sim1_sim2_compare['S2'])
outputs_reports_comparisonReport['S2_ssq_sim1exp'] = np.array(tasks_sim1_exp_compare['S2'])
outputs_reports_comparisonReport['S2_ssq_sim2exp'] = np.array(tasks_sim2_exp_compare['S2'])
print(outputs_reports_comparisonReport)

# Output comparisonSummary:
outputs_reports_comparisonSummary = tasks_compare_summary
print(outputs_reports_comparisonSummary)

# Output Fig1:
fig, ax = plt.subplots()
ys = np.vstack((tasks_sim1['S1'], tasks_sim1['S2'], tasks_sim2['S1'], tasks_sim2['S2'], inputs_data_experiment1['S1'], inputs_data_experiment1['S2'], ))
ys = ys.transpose()
x = tasks_sim1['time']
ax.plot(x, ys)
ax.set(xlabel='Time', ylabel='Concentrations', title='Figure 1')
plt.show()""".strip()

ex2 = Path(root_dir, "examples", "two", "example.xml")
expected_python_ex_2 = """
import numpy as np


# Translation of SED document vSED v2.0 alpha to python

# All tasks:

# Task model1:
inputs_models_model1 = r'""" + str(ex2) + """'

# Task scan_k1_and_k2:

# All Outputs:

# Output steadyStateReport:
outputs_reports_steadyStateReport = tasks_scan_k1_and_k2_subTasks_steadyState
print(outputs_reports_steadyStateReport)

# Output jacobianReport:
outputs_reports_jacobianReport = tasks_scan_k1_and_k2_subTasks_jacobians
print(outputs_reports_jacobianReport)

# Output Fig1:
""".strip()


def test_python_transpile_ex_1(tmp_path):
    root_dir = Path(__file__).resolve().parents[1]
    context = {"tasks": {"sim2": "Copasi"}}
    python1 = transpile(root_dir / "examples/one/", "sed.json", context)

    # print("Exported python:")
    # print("-----")
    # print(python1.strip())
    # print("-----")
    # print("Expected python:")
    # print(expected_python_ex_1)
    # print("-----")
    assert python1.strip() == expected_python_ex_1.strip()

    script = tmp_path / "t.py"
    script.write_text(python1, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True, text=True, timeout=500,
        env={**os.environ, "MPLBACKEND": "Agg"},
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "expected"

def test_python_transpile_ex_2(tmp_path):
    root_dir = Path(__file__).resolve().parents[1]

    python2 = transpile(root_dir / "examples/two/", "sed.json")
    # print("Exported python:")
    # print(python2.strip())
    # print("-----")
    # print("Expected python:")
    # print(expected_python_ex_2)
    # print("-----")
    assert expected_python_ex_2.strip() == python2.strip()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])