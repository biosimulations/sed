from sed.transpiler import load_sed


def test_transpile():
    document = load_sed("tests/examples/one/")

    print(document)



