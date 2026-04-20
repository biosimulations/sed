import re

from sed.transpiler.library import parse_hash
from base import SEDBase, Range
import pandas as pd
from pathlib import Path
#from typing import Any


class AbstractTask(SEDBase):
    """The base class for all tasks."""

    def __init__(self, config: dict):
        super().__init__(self, config)
        self.kisaoID = config.pop("kisaoID", None)
        self.altDefinition = config.pop("altDefinition", None)
        #TODO: make actual list of AlgorithmParameter objects
        self.algorithmParameters = config.pop("algorithmParameters", None)
        self.validate(config)

    def validate(self, leftovers={}):
        """Validate."""
        #TODO: check if kisao is valid, and if altDefinition is URI.
        return False
    

class ModelImport(AbstractTask):
    """A 'modelImport' object, used as input for simulators."""

    def __init__(self, config: dict):
        super().__init__(self, config)
        self.location = config.pop("location", None)
        self.language = config.pop("language", None)
        self.validate(config)

    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Model:", leftovers)
            return True
        return False

    def make_python(self, key, root_dir):
        headers = set()
        code = "inputs_models_" + key + " = r'" + str(Path(root_dir) / self.location) + "'\n"
        return headers, code

    # No processing, pass the file location to appropiate step/process
    # For each reference to model in question, replace with file location
    # (In reference to specific task in question, and its config)
    # (ex. UTCCopais config: model_path=[said model])
    def load_model(self, root_dir):
        # TODO: error handling
        path = root_dir / self.location
        language = self.language
        model = {"filepath": path, "language": language}
        return model


class DataImport(AbstractTask):
    """A 'dataImport' object, used to import data from a file."""

    def __init__(self, config: dict):
        super().__init__(self, config)
        self.location = config.pop("location", None)
        self.format = config.pop("format", None)
        self.parameters = config.pop("parameters", None)
        self.validate(config)
        self.MEDIA_TYPES = {"http://purl.org/NET/mediatypes/text/csv": self.load_csv}

    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Data:", leftovers)
            return True
        return False

    def load(self, root):
        return self.MEDIA_TYPES[self.format](root)

    def load_csv(self, root):
        # TODO: deal with parameters (!)
        df = pd.read_csv(root / self.location)
        return {key: list(series) for key, series in df.items()}

    def make_python(self, key, root_dir):
        if self.format == "http://purl.org/NET/mediatypes/text/csv":
            headers = set(["import pandas as pd"])
            code = "inputs_data_" + key + " = pd.read_csv(r'" + str(Path(root_dir) / self.location) + "')\n"
            return headers, code
        else:
            raise ValueError("Unable to translate reading data in format '" + self.format + "'.")

    def load_data(self, root):
        # TODO: deal with all error handling (!)

        load_file = self.MEDIA_TYPES[self.format]
        path = root / self.location
        data = load_file(path, self.parameters)

        return data


class ODESimulation(AbstractTask):
    """The definition of a uniform time course simulation."""

    def __init__(self, config: dict):
        # TODO: error checking
        self.type_key = "explicitODESimulation"
        self.model = config.pop("model", None)
        self.independentVariable = config
        self.independentVariableRange = Range(config.pop("independentVariableRange", {}))
        self.outputVariables = config.pop("outputVariables", None)
        self.initialTime = config.pop("initialTime", None)
        self.validate(config)
        self.executor = "Tellurium"

    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating explicitODESimulation:", leftovers)
            return True
        return False

class ExplicitODESimulation(ODESimulation):
    """The definition of a uniform time course simulation."""

    def __init__(self, config: dict):
        # TODO: error checking
        super().init(self, config)
        self.type_key = "explicitODESimulation"
        self.model = config.pop("model", None)
        self.independentVariable = config.pop("independentVariable", None)
        self.independentVariableInit = config.pop("independentVariableInit", None)
        self.independentVariableRange = Range(config.pop("independentVariableRange", {}))
        self.outputVariables = config.pop("outputVariables", None)
        self.initialTime = config.pop("initialTime", None)
        self.validate(config)
        self.executor = "Tellurium"

    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating explicitODESimulation:", leftovers)
            return True
        return False

    def make_python(self, key):
        if self.executor == "Tellurium":
            return self.make_python_tellurium(key)
        elif self.executor == "Copasi":
            return self.make_python_copasi(key)
        else:
            raise ValueError("Unknown uniform time course executor '" + self.executor + "'")

    def make_python_tellurium(self, key):
        if self.independentVariable != "urn:sedml:symbol:time":
            print("Unable to simulate with tellurium: independent variable is not 'time'.")
            return
        headers = set(["import tellurium as te"])
        modelid = self.model
        modelid = self.model[1:]
        modelid = modelid.replace(":", "_")
        taskid = "tasks_" + key
        code = taskid + "_r = te.loadSBMLModel(" + modelid + ")\n"
        code += (
            taskid
            + " = "
            + taskid
            + "_r.simulate("
            + str(self.independentVariableRange.start)
            + ", "
            + str(self.independentVariableRange.end)
            + ", steps="
            + str(self.independentVariableRange.numberOfSteps)
            + ", selections = "
            + str(['time'] + self.outputVariables)
            + ")\n"
        )
        return headers, code

    def make_python_copasi(self, key):
        # copasi_df: DataFrame = basico.run_time_course(
        #     start_time=0,
        #     duration=20,
        #     intervals=50,
        #     update_model=True,
        #     use_sbml_id=True,
        #     model=basico.load_model(str(example_one_dir / "example1.xml"))
        # )
        # copasi_out = {}
        # copasi_out["time"] = np.array(copasi_df.index)
        # copasi_out["S1"] = np.array(copasi_df["S1"])
        # copasi_out["S2"] = np.array(copasi_df["S2"])
        # copasi_out = DataFrame(copasi_out)
        if self.independentVariable != "urn:sedml:symbol:time":
            print("Unable to simulate with tellurium: independent variable is not 'time'.")
            return
        headers = set(["import basico"])
        headers.add("import numpy as np")
        headers.add("from pandas import DataFrame")
        modelid = self.model
        modelid = self.model[1:]
        modelid = modelid.replace(":", "_")
        taskid = "tasks_" + key
        code = (
            taskid
            + "_copasi = basico.run_time_course(start_time="
            + str(self.independentVariableRange.start)
            + ", duration="
            + str(self.independentVariableRange.end - self.timeRange.start)
            + ", intervals="
            + str(self.independentVariableRange.numberOfSteps)
            + ", update_model=True, use_sbml_id=True,model=basico.load_model("
            + modelid
            + "))\n"
        )
        code += taskid + " = {}\n"
        first = 0
        if self.outputVariables[0] == "time":
            first = 1
            code += taskid + "['time'] = np.array(" + taskid + "_copasi.index)\n"
        for var in self.outputVariables[first:]:
            code += taskid + "['" + var + "'] = np.array(" + taskid + "_copasi['" + var + "'])\n"
        code += taskid + " = DataFrame(" + taskid + ")\n"
        return headers, code

    def default_step_name(self):
        return "pbest.registry.simulators.tellurium_process.TelluriumUTCStep"

    def make_inputs_schema(self):
        return {"model": {"filepath": "string", "language": "string"}}

    def make_inputs(self):
        return {"model_source": parse_hash(self.model)}

    def make_outputs_schema(self):
        outputs = {}
        for key in self.outputVariables:
            outputs[key] = "array[float]"
        return outputs

    def make_outputs(self, task_key):
        outputs = {}
        for key in self.outputVariables:
            outputs[key] = ["results", task_key, key]
        return outputs


class Calculation(AbstractTask):
    """The definition of a 'calculation' task, which performs a calulation on inputs."""

    def __init__(self, config: dict):
        # TODO: error checking
        super().__init__(self, config)
        self.type_key = "Calculation"
        self.infix = config.pop("math", None)
        self.units = config.pop("units", None)
        self.validate(config)
        # self.visitor = default_math_visitor()
        # self.expression = visit_expression(self.infix, self.visitor)

    def __str__(self):
        ret = "Calculation object.  Infix: '" + self.infix + "'\n"
        if self.units:
            ret += "Units: '" + self.units + "'\n"
        return ret.strip()

    def __repr__(self):
        return self.__str__()

    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Calculation:", leftovers)
            return True
        return False

    def getInputVariables(self):
        """Parse the infix to retrieve all SED variable inputs."""
        strlist = re.findall(r"#[a-zA-Z0-9_:.]*", self.infix)
        return set(strlist)

    def make_python(self, key):
        headers = set()
        line = self.infix.replace(":", "_")
        line = line.replace("#", "")
        line = line.replace("^", "**")
        code = "tasks_" + key + " = " + line + "\n"
        return headers, code

    def default_step_name(self):
        return "MathExpressionStep"

    def make_inputs_schema(self):
        import ipdb

        ipdb.set_trace()

        return dict.fromkeys(self.visitor.symbol_paths, "array[float]")

    def make_inputs(self):
        return {key: path for key, path in self.visitor.symbol_paths.items()}

    def make_outputs_schema(self):
        outputs = {}
        for key in self.outputVariables:
            outputs[key] = "array[float]"
        return outputs

    def make_outputs(self, task_key):
        outputs = {}
        for key in self.outputVariables:
            outputs[key] = ["results", task_key, key]
        return outputs


class SumOfSquares(AbstractTask):
    """The definition of a 'sumOfSquares' task, which calculates the differences between inputs."""

    def __init__(self, config: dict):
        super().__init__(self, config)
        self.type_key = "SumOfSquares"
        self.inputs = config.pop("inputs", None)
        self.validate(config)

    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating SumOfSquares:", leftovers)
            return True
        return False

    def make_python(self, key):
        headers = set()
        code = ""
        return headers, code


class ParameterScan(AbstractTask):
    """The definition of a 'parameter scan' task, which takes a model as input and outputs an array of models."""

    def __init__(self, config: dict):
        self.type_key = "ParameterScan"
        super().__init__(self, config)
        self.model = config.pop("model", None)
        self.scannedVariable = config.pop("scannedVariable", None)
        self.range = Range(config.pop("range", {}))
        self.outputRange = config.pop("outputRange", None)
        self.validate(config)

    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating ParameterScan:", leftovers)
            return True
        return False

    def make_python(self, key):
        headers = set()
        code = ""
        return headers, code


class SteadyState(AbstractTask):
    """The definition of a 'parameter scan' task, which takes a model as input and outputs an array of models."""

    def __init__(self, config: dict):
        super().__init__(self, config)
        self.type_key = "SteadyState"
        self.model = config.pop("model", None)
        self.outputVariables = config.pop("outputVariables", None)
        self.outputModel = config.pop("outputModel", None)
        self.validate(config)

    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating SteadyState:", leftovers)
            return True
        return False

    def exportToProcessBigraph():
        """foo"""
        pass

    def make_python(self, key):
        headers = set()
        code = ""
        return headers, code


def load_tasks_section(tasks_section_config):
    tasks = {}
    for key, config in tasks_section_config.items():
        step_type = config.pop("_type", None)
        match step_type:
            case "modelImport":
                tasks[key] = ModelImport(config)
            case "dataImport":
                tasks[key] = DataImport(config)
            case "explicitODESimulation":
                tasks[key] = ExplicitODESimulation(config)
            case "calculation":
                tasks[key] = Calculation(config)
            case "sumOfSquares":
                tasks[key] = SumOfSquares(config)
            case "parameterScan":
                tasks[key] = ParameterScan(config)
            case "steadyState":
                tasks[key] = SteadyState(config)
            case None:
                raise ValueError("No '_type' provided for task " + key + ".")
            case _:
                print(f"unknown task type: {step_type}")
                # raise ValueError("Unknown task type " + step_type + ".")
    return tasks
