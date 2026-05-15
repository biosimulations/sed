import json
from pathlib import Path

from bigraph_schema import allocate_core
from process_bigraph import Composite

from sed.transpiler import transpile_to_pbg as transpile_to_pbg

def test_pbg_transpile():
    root_dir = Path(__file__).parents[1]
    context = {"tasks": {"sim2": "pbest.registry.simulators.copasi_process.CopasiUTCStep"}, "root_dir": root_dir}

    pbg1 = transpile_to_pbg.transpile(root_dir / "examples/one/", "sed.json", context)
    core = allocate_core()
    composite = Composite(core=core, config=pbg1)
    print(json.dumps(pbg1, indent=4))


