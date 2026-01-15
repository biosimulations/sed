from pathlib import Path
from typing import Any

class Axis(object):
    """A 'plot' object, used to define a 2D visual representation of data."""

    def __init__(self, axis_config: dict):
        self.label = axis_config.pop("label", None)
        self.scale = axis_config.pop("scale", None)
        self.validate(axis_config)
    
    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Axis:", leftovers)
            return True
        return False


class Curve(object):
    """A 'curve' object, used in plots to define data traces."""

    def __init__(self, curve_config: dict):
        self.x = curve_config.pop("x", None)
        self.y = curve_config.pop("y", None)
        self.style = curve_config.pop("style", None)
        self.validate(curve_config)
    
    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Curve:", leftovers)
            return True
        return False


class Surface(object):
    """A 'curve' object, used in plots to define data traces."""

    def __init__(self, surface_config: dict):
        self.x = surface_config.pop("x", None)
        self.y = surface_config.pop("y", None)
        self.z = surface_config.pop("z", None)
        self.style = surface_config.pop("style", None)
        self.validate(surface_config)
    
    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Curve:", leftovers)
            return True
        return False


class Plot(object):
    """A 'plot' object, used to define a 2D visual representation of data."""

    def __init__(self, plot_config: dict):
        self.label = plot_config.pop("label", None)
        self.height = plot_config.pop("height", None)
        self.width = plot_config.pop("width", None)
        self.legend = plot_config.pop("legend", None)
        self.xaxis = Axis(plot_config.pop("xAxis", {}))
        self.yaxis = Axis(plot_config.pop("yAxis", {}))

    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Plot2D:", leftovers)
            return True
        return False
    
    
class Plot2D(Plot):
    """A 'plot' object, used to define a 2D visual representation of data."""

    def __init__(self, plot_config: dict):
        super().__init__(plot_config)
        self.rightYAxis = Axis(plot_config.pop("rightYAxis", {}))
        curves = plot_config.pop("curves", {})
        self.curves = {}
        if (curves):
            for key, config in curves.items():
                self.curves[key] = Curve(config)
        self.validate(plot_config)

    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Plot2D:", leftovers)
            return True
        return False
    
    
class Plot3D(Plot):
    """A 'plot' object, used to define a 2D visual representation of data."""

    def __init__(self, plot_config: dict):
        super().__init__(plot_config)
        self.zAxis = Axis(plot_config.pop("zAxis", {}))
        surfaces = plot_config.pop("surfaces", {})
        self.surfaces = {}
        if (surfaces):
            for key, config in surfaces.items():
                self.surfaces[key] = Surface(config)
        self.validate(plot_config)

    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Plot2D:", leftovers)
            return True
        return False
    
    
class DataSet(object):
    """A data set, to be exported in a Report."""

    def __init__(self, dataset_config: dict):
        self.label = dataset_config.pop("label", None)
        self.xaxis = Axis(dataset_config.pop("xaxis", {}))
        self.yaxis = Axis(dataset_config.pop("yaxis", {}))
        curves = dataset_config.pop("curves", {})
        self.curves = {}
        if (curves):
            for key, config in curves.items():
                self.curves[key] = Curve(config)
        self.validate(dataset_config)

    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating DataSet:", leftovers)
            return True
        return False
    

class Report(object):
    """A 'report' object, for storing and reporting data."""
    #TODO: Make a Plot3D class and a Plot class for the overlap.

    def __init__(self, report_config: dict):
        self.filename = report_config.pop("filename", None)
        self.file_format = report_config.pop("file_format", None)
        self.dataSets = report_config.pop("dataSets", None)
        self.validate(report_config)

    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Report:", leftovers)
            return True
        return False


class Style(object):
    """A style defined for visual representation of something in a plot (i.e. a curve or an axis)"""

    def __init__(self, style_config: dict):
        self.line = style_config.pop("line", None)
        self.markers = style_config.pop("markers", None)
        self.validate(style_config)

    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Style:", leftovers)
            return True
        return False


def load_outputs_section(output_section: dict[Any, Any]):
    outputs = {}
    outputs["reports"] = {}
    outputs["plots"] = {}
    outputs["styles"] = {}
    
    for key, config in output_section.pop("reports", {}).items():
        outputs["reports"][key] = Report(config)

    for key, config in output_section.pop("plots", {}).items():
        plot_type = config.pop("_type", None)
        match plot_type:
            case "plot2D":
                outputs["plots"][key] = Plot2D(config)
            case "plot3D":
                outputs["plots"][key] = Plot3D(config)
            case None:
                raise ValueError("No '_type' provided for plot " + key + ".")
            case _:
                raise ValueError("Unknown plot type " + plot_type + ".")
                

    for key, config in output_section.pop("styles", {}).items():
        outputs["styles"][key] = Style(config)

    if len(output_section):
        print("Unsaved data when creating Axis:", output_section)
    
    return outputs
