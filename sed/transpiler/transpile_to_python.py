import json
import logging
from pathlib import Path
from typing import Any

from sed.transpiler.importers.document import SedDocument

logger = logging.getLogger(__name__)

# from pbest import CompositeBuilder


# TODO: need to import the database
#   containing information about the
#   different task types and their
#   available inputs and outputs

# TODO: provide a way to validate the
#   document directly without needing to
#   actually run it (???)


def load_sed(sed: dict[Any, Any], root_dir=None, context={}) -> dict[str, Any]:
    root_dir = Path(root_dir or ".")

    seddoc = SedDocument(sed)

    logger.debug(seddoc)
    logger.debug("")

    return seddoc


def translate_to_python(seddoc: SedDocument, context, path):
    headers, python = seddoc.exportToPython(context, path)

    headers = sorted(list(headers))
    ret = ""
    for header in headers:
        ret += header + "\n"
    ret += "\n\n" + python

    return ret


def transpile(path, filename, context={}):
    path = Path(path)
    sed_path = path / filename

    with open(sed_path) as sed_file:
        sed = json.load(sed_file)

    seddoc = load_sed(sed, path)
    logger.debug(seddoc)
    python = translate_to_python(seddoc, context, path)
    return python


if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parents[2]
    context = {"tasks": {"sim2": "Copasi"}}
    python1 = transpile(root_dir / "examples/one/", "sed.json", context)
    print("")
    print(python1)
    print("")

    python2 = transpile(root_dir / "examples/two/", "sed.json")
    print("")
    print(python2)
