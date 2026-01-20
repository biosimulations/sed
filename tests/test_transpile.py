import pbest.globals
from process_bigraph import Composite

from sed.transpiler.transpiler import transpile
from tests.utils import PROJECT_ROOT_DIR


def test_transpile_to_pb_comparison():
    pb_document = transpile(f"{PROJECT_ROOT_DIR}/examples/one/", "sed.json")

    core = pbest.globals.get_loaded_core()
    composite = Composite(core=core, config={"state": pb_document})

    composite.run(1)

    print(composite.serialize_state())




