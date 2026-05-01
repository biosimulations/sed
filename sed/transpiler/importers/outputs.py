from typing import Any
from sed.transpiler.importers.base import SedBase, str_to_py_str


class Axis(SedBase):
    """A 'plot' object, used to define a 2D visual representation of data."""

    def __init__(self, config: dict):
        self.label = config.pop("label", None)
        self.scale = config.pop("scale", None)
        self.__validate(config)

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Axis:", leftovers)
            return True
        return False


class Curve(SedBase):
    """A 'curve' object, used in plots to define data traces."""

    def __init__(self, config: dict):
        self.x = config.pop("x", None)
        self.y = config.pop("y", None)
        self.style = config.pop("style", None)
        self.__validate(config)

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Curve:", leftovers)
            return True
        return False


class Surface(SedBase):
    """A 'curve' object, used in plots to define data traces."""

    def __init__(self, config: dict):
        self.x = config.pop("x", None)
        self.y = config.pop("y", None)
        self.z = config.pop("z", None)
        self.style = config.pop("style", None)
        self.__validate(config)

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Curve:", leftovers)
            return True
        return False

class Output(SedBase):
    """The base class for all Output objects."""
    def __init__(self, config: dict):
        self.kisaoID = config.pop("kisaoID", None)
        self.altDefinition = config.pop("altDefinition", None)
        self.algorithmParameters = config.pop("algorithmParameters", None)

    def __validate(self, leftovers={}):
        """Validate."""
        return False

class Plot(Output):
    """A 'plot' object, used to define a 2D visual representation of data."""

    def __init__(self, config: dict):
        self.label = config.pop("label", None)
        self.height = config.pop("height", None)
        self.width = config.pop("width", None)
        self.legend = config.pop("legend", None)
        self.xaxis = Axis(config.pop("xAxis", {}))
        self.yaxis = Axis(config.pop("yAxis", {}))

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Plot2D:", leftovers)
            return True
        return False


class Plot2D(Plot):
    """A 'plot' object, used to define a 2D visual representation of data."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.rightYAxis = Axis(config.pop("rightYAxis", {}))
        curves = config.pop("curves", {})
        self.curves = {}
        if curves:
            for key, config in curves.items():
                self.curves[key] = Curve(config)
        self.__validate(config)

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Plot2D:", leftovers)
            return True
        return False

    def exportToPython(self, key, root_dir):
        headers = set(["import matplotlib.pyplot as plt"])
        code = "fig, ax = plt.subplots()\n"
        xref = ""
        ys = []
        code += "ys = np.vstack(("
        for curve in self.curves:
            y = str_to_py_str(self.curves[curve].y)
            ys.append(y)
            code += y + ", "
            # TODO: check to make sure all xrefs are the same
            xref = str_to_py_str(self.curves[curve].x)
        code += "))\nys = ys.transpose()\n"
        code += "x = " + xref + "\n"
        code += "ax.plot(x, ys)\n"
        ax_args = ""
        if self.xaxis:
            ax_args += "xlabel='" + self.xaxis.label + "'"
        if self.yaxis:
            ax_args += ", ylabel='" + self.yaxis.label + "'"
        if self.label:
            ax_args += ", title='" + self.label + "'"
        code += f"ax.set({ax_args})\n"
        code += f"plt.savefig('{key}.png')\n"
        code += "plt.show()\n"

        return headers, code


class Plot3D(Plot):
    """A 'plot' object, used to define a 2D visual representation of data."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.zAxis = Axis(config.pop("zAxis", {}))
        surfaces = config.pop("surfaces", {})
        self.surfaces = {}
        if surfaces:
            for key, config in surfaces.items():
                self.surfaces[key] = Surface(config)
        self.__validate(config)

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Plot2D:", leftovers)
            return True
        return False

    def exportToPython(self, key, root_dir):
        headers = set()
        code = ""
        return headers, code


class Report(Output):
    """A 'report' object, for storing and reporting data."""

    def __init__(self, config: dict):
        self.filename = config.pop("filename", None)
        self.file_format = config.pop("file_format", None)
        self.dataSets = config.pop("dataSets", None)
        self.__validate(config)

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Report:", leftovers)
            return True
        return False

    def exportToPython(self, key, root_dir):
        headers = set(["import numpy as np", "import pandas as pd"])
        repid = "outputs_" + key
        code = ""
        if isinstance(self.dataSets, str):
            line = str_to_py_str(self.dataSets)
            code = "header = True\n"
            code += repid + " = " + line + "\n"
            headers.add("import collections")
            code += f"if isinstance({repid}, (collections.abc.Mapping, pd.DataFrame)):\n"
            code += f"   for key in {repid}:\n"
            code += f"      {repid}[key] = np.atleast_1d({repid}[key])\n"
            code +=  "else:\n"
            code +=  "   header = False\n"
            code += f'pd.DataFrame({repid}).to_csv("{repid}.csv", index=False, header=header)\n'
        else:
            code += repid + " = {}\n"
            for ds_key in self.dataSets:
                line = str_to_py_str(self.dataSets[ds_key])
                code += repid + "['" + ds_key + "'] = np.atleast_1d(" + line + ")\n"
            #code += "print(" + repid + ")\n"
            code += f'pd.DataFrame({repid}).to_csv("{repid}.csv", index=False)\n'
        return headers, code


class Style(SedBase):
    """A style defined for visual representation of something in a plot (i.e. a curve or an axis)"""

    def __init__(self, config: dict):
        self.line = config.pop("line", None)
        self.markers = config.pop("markers", None)
        self.__validate(config)

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Style:", leftovers)
            return True
        return False


def load_outputs_section(output_section: dict[Any, Any]):
    outputs = {}
    for key, config in output_section.items():
        step_type = config.pop("_type", None)
        match step_type:
            case "report":
                outputs[key] = Report(config)
            case "plot2D":
                outputs[key] = Plot2D(config)
            case "plot3D":
                outputs[key] = Plot3D(config)
            case None:
                raise ValueError("No '_type' provided for task " + key + ".")
            case _:
                print(f"unknown output type: {step_type}")
                # raise ValueError("Unknown task type " + step_type + ".")
    return outputs
