import json

from sed.transpiler import load_sed






def test_transpile_to_pb_comparison():
    document = load_sed("examples/one/")

    with open("test.json", "w") as f:
        f.write(json.dumps(document))




