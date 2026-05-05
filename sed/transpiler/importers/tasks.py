import re

from pbest import CompositeBuilder

from sed.transpiler.library import parse_hash
from sed.transpiler.importers.base import SedBase, Range, Span, LoopVariable, from_attribute_to_list_path, str_to_py_str
import pandas as pd
from pathlib import Path
#from typing import Any


class AbstractTask(SedBase):
    """The base class for all tasks."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.kisaoID = config.pop("kisaoID", None)
        self.altDefinition = config.pop("altDefinition", None)
        #TODO: make actual list of AlgorithmParameter objects
        self.algorithmParameters = config.pop("algorithmParameters", None)
        self.__validate(config)

    def __validate(self, leftovers={}):
        """Validate."""
        #TODO: check if kisao is valid, and if altDefinition is URI.
        return False
    

class ModelImport(AbstractTask):
    """A 'modelImport' object, used as input for simulators."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.location = config.pop("location", None)
        self.language = config.pop("language", None)
        self.__validate(config)

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating ModelImport:", leftovers)
            return True
        return False

    def exportToPBG(self, key, builder: CompositeBuilder, root_dir):
        list_path: list[str] = from_attribute_to_list_path(f"#tasks:{key}.model")

        dict_in_q = builder.get_builder_state()
        for k in range(len(list_path)):
            if k == len(list_path) - 1 and k in dict_in_q:
                raise ValueError(f"Path should not have any values in it. Path: {list_path}, State: {builder.get_builder_state()}")
            elif k == len(list_path) - 1:
                dict_in_q[k] = self.location
            elif k in dict_in_q:
                dict_in_q = dict_in_q[k]
            else:
                dict_in_q[k] = {}



    def exportToPython(self, key, root_dir):
        headers = set(["import tellurium as te"])
        code = f"{str_to_py_str(key)}_model = te.loadSBMLModel(r'{str(Path(root_dir) / self.location)}')\n"
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
        super().__init__(config)
        self.location = config.pop("location", None)
        self.format = config.pop("format", None)
        self.parameters = config.pop("parameters", None)
        self.__validate(config)
        self.MEDIA_TYPES = {"http://purl.org/NET/mediatypes/text/csv": self.load_csv}

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating DataImport:", leftovers)
            return True
        return False

    def load(self, root):
        return self.MEDIA_TYPES[self.format](root)

    def load_csv(self, root):
        # TODO: deal with parameters (!)
        df = pd.read_csv(root / self.location)
        return {key: list(series) for key, series in df.items()}

    def exportToPython(self, key, root_dir):
        if self.format == "http://purl.org/NET/mediatypes/text/csv":
            headers = set(["import pandas as pd"])
            code = f"{str_to_py_str(key)} = pd.read_csv(r'{str(Path(root_dir) / self.location)}')\n"
            return headers, code
        else:
            raise ValueError(f"Unable to translate reading data in format '{self.format}'.")

    def load_data(self, root):
        # TODO: deal with all error handling (!)

        load_file = self.MEDIA_TYPES[self.format]
        path = root / self.location
        data = load_file(path, self.parameters)

        return data


class AggregationCalculation(AbstractTask):
    """An 'aggregationCalculation' object, used for calculations of average, max, etc.  Also used for defined export variables from a Loop.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.type_key = "aggregationCalculation"
        self.input = config.pop("input", None)
        self.__validate(config)

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating AggregationCalculation:", leftovers)
            return True
        return False


class ODESimulation(AbstractTask):
    """The definition of a uniform time course simulation."""

    def __init__(self, config: dict):
        super().__init__(config)
        # TODO: error checking
        self.model = config.pop("model")
        self.independentVariable = config.pop("independentVariable", None)
        self.independentVariableInit = config.pop("independentVariableInit", None)
        self.outputVariables = config.pop("outputVariables", None)
        self.outputModel = config.pop("outputModel", None)
        self.__validate(config)
        self.executor = "Tellurium"

    def __validate(self, leftovers={}):
        """Validate."""
        # if len(leftovers):
        #     print("Unsaved data when creating explicitODESimulation:", leftovers)
        #     return True
        return False

    def setContext(self, val):
        self.executor = val;

class ExplicitODESimulation(ODESimulation):
    """The definition of a uniform time course simulation."""

    def __init__(self, config: dict):
        # TODO: error checking
        super().__init__(config)
        self.type_key = "explicitODESimulation"
        self.independentVariableRange = Range(config.pop("independentVariableRange", {}))
        self.__validate(config)
        self.executor = "Tellurium"

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating explicitODESimulation:", leftovers)
            return True
        return False

    def exportToPython(self, key, root_dir):
        if self.executor == "Tellurium":
            return self.exportToPython_tellurium(key)
        elif self.executor == "Copasi":
            return self.exportToPython_copasi(key)
        else:
            raise ValueError(f"Unknown uniform time course executor '{self.executor}'")

    def exportToPython_tellurium(self, key):
        if self.independentVariable != "urn:sedml:symbol:time":
            print("Unable to simulate with tellurium: independent variable is not 'time'.")
            return
        headers = set(["import tellurium as te", "import pandas as pd"])
        modelid = str_to_py_str(self.model)
        taskid = str_to_py_str(key)
        code = f"{taskid}_model = te.loadSBMLModel({modelid}.getCurrentSBML())\n"
        code += (
            f"{taskid} = {taskid}_model.simulate("
            f"{self.independentVariableRange.start}, "
            f"{self.independentVariableRange.end}, "
            f"steps = {self.independentVariableRange.numberOfSteps}, "
            f"selections = {['time'] + self.outputVariables})\n"
        )
        # Convert to pandas dataframe
        code += f"{taskid} = pd.DataFrame({taskid}, columns={taskid}.colnames)\n"
        return headers, code

    def exportToPython_copasi(self, key):
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
        modelid = str_to_py_str(self.model)
        taskid = str_to_py_str(key)
        code = (
            f"{taskid}_copasi = basico.run_time_course("
            f"start_time = {self.independentVariableRange.start}, "
            f"duration = {self.independentVariableRange.end - self.independentVariableRange.start}, "
            f"intervals = {self.independentVariableRange.numberOfSteps}, "
            f"update_model = True, "
            f"use_sbml_id = True, "
            f"model = basico.load_model({modelid}.getCurrentSBML()))\n"
        )
        code += f"{taskid} = {{}}\n"
        first = 0
        if self.outputVariables[0] == "time":
            first = 1
            code += f"{taskid}['time'] = np.array({taskid}_copasi.index)\n"
        for var in self.outputVariables[first:]:
            code += f"{taskid}['{var}'] = np.array({taskid}_copasi['{var}'])\n"
        code += f"{taskid} = DataFrame({taskid})\n"
        return headers, code

    # Chain problem,
    # Get model,
    # SED provides start, end, num_steps, initialValue, model, outputVariables (we'll probably output everything for now)
    # PBG Requires model source, time, n_steps, output dir
    def zekes_case(self, builder: CompositeBuilder) -> CompositeBuilder:

        inputs = {
            "model": from_attribute_to_list_path(self.model),
            "independentVariable": from_attribute_to_list_path(self.independentVariableRange)
        }
        outputs = {}

        # builder.add_step(address=self.executor, config={}, inputs=)
        builder.add_step(
            address="TelluriumUTCStep",
            config={"model_source": self.model, "time": self.independentVariableRange.end,
                    "n_points": self.independentVariableRange.numberOfSteps, "output_dir": ""},
            inputs={},
            outputs={"result": ['sim', 'tellurium']}
        )
        return builder

    # Worry about conflicts higher up
    def logans_case(self) -> dict[str, str]:
        return {}

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


class BoundedODESimulation(ODESimulation):
    """The definition of a uniform time course simulation."""

    def __init__(self, config: dict):
        # TODO: error checking
        super().__init__(config)
        self.type_key = "boundedODESimulation"
        self.independentVariableSpan = Span(config.pop("independentVariableSpan", {}))
        self.__validate(config)
        self.executor = "Tellurium"

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating boundedODESimulation:", leftovers)
            return True
        return False

    def exportToPython(self, key, root_dir):
        if self.executor == "Tellurium":
            return self.exportToPython_tellurium(key)
        elif self.executor == "Copasi":
            raise ValueError("Copasi export not yet implemented.")
        else:
            raise ValueError(f"Unknown uniform time course executor '{self.executor}'")

    def exportToPython_tellurium(self, key):
        if self.independentVariable != "urn:sedml:symbol:time":
            print("Unable to simulate with tellurium: independent variable is not 'time'.")
            return
        headers = set(["import tellurium as te", "import pandas as pd"])
        modelid = str_to_py_str(self.model)
        taskid = str_to_py_str(key)
        code = f"{taskid}_model = te.loadSBMLModel({modelid}.getCurrentSBML())\n"
        code += (
            f"{taskid} = {taskid}_model.simulate("
            f"{self.independentVariableSpan.start}, "
            f"{self.independentVariableSpan.end}, "
            f"selections = {['time'] + self.outputVariables})\n"
        )
        # Convert to pandas dataframe
        code += f"{taskid} = pd.DataFrame({taskid}, columns={taskid}.colnames)\n"
        return headers, code

    def exportToPython_copasi(self, key):
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
        modelid = str_to_py_str(self.model)
        taskid = str_to_py_str(key)
        code = (
            f"{taskid}_copasi = basico.run_time_course("
            f"start_time = {self.independentVariableRange.start}, "
            f"duration = {self.independentVariableRange.end - self.independentVariableRange.start}, "
            f"intervals = {self.independentVariableRange.numberOfSteps}, "
            f"update_model = True, "
            f"use_sbml_id = True, "
            f"model = basico.load_model({modelid}.getCurrentSBML()))\n"
        )
        code += f"{taskid} = {{}}\n"
        first = 0
        if self.outputVariables[0] == "time":
            first = 1
            code += f"{taskid}['time'] = np.array({taskid}_copasi.index)\n"
        for var in self.outputVariables[first:]:
            code += f"{taskid}['{var}'] = np.array({taskid}_copasi['{var}'])\n"
        code += f"{taskid} = DataFrame({taskid})\n"
        return headers, code


class StochasticSimulation(AbstractTask):
    """The base class for a stochastic simulation."""

    def __init__(self, config: dict):
        super().__init__(config)
        # TODO: error checking
        self.model = config.pop("model")
        self.independentVariable = config.pop("independentVariable", None)
        self.independentVariableInit = config.pop("independentVariableInit", None)
        self.outputVariables = config.pop("outputVariables", None)
        self.outputModel = config.pop("outputModel", None)
        self.__validate(config)
        self.executor = "Tellurium"

    def __validate(self, leftovers={}):
        """Validate."""
        # if len(leftovers):
        #     print("Unsaved data when creating explicitODESimulation:", leftovers)
        #     return True
        return False

    def setContext(self, val):
        self.executor = val;

class ExplicitStochasticSimulation(ODESimulation):
    """The definition of a stochastic simulation with explicit output points."""

    def __init__(self, config: dict):
        # TODO: error checking
        super().__init__(config)
        self.type_key = "explicitStochasticSimulation"
        self.independentVariableRange = Range(config.pop("independentVariableRange", {}))
        self.__validate(config)
        self.executor = "Tellurium"

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating explicitStochasticSimulation:", leftovers)
            return True
        return False

    def exportToPython(self, key, root_dir):
        if self.executor == "Tellurium":
            return self.exportToPython_tellurium(key)
        elif self.executor == "Copasi":
            raise ValueError("Copasi implementation of stochastic simulation is not yet implemented.")
        else:
            raise ValueError(f"Unknown uniform time course executor '{self.executor}'")

    def exportToPython_tellurium(self, key):
        if self.independentVariable != "urn:sedml:symbol:time":
            print("Unable to simulate with tellurium: independent variable is not 'time'.")
            return
        headers = set(["import tellurium as te", "import pandas as pd"])
        modelid = str_to_py_str(self.model)
        taskid = str_to_py_str(key)
        code = f"{taskid}_model = te.loadSBMLModel({modelid}.getCurrentSBML())\n"
        code += f"{taskid}_model.setIntegrator('gillespie')\n"
        code += (
            f"{taskid} = {taskid}_model.simulate("
            f"{self.independentVariableRange.start}, "
            f"{self.independentVariableRange.end}, "
            f"steps = {self.independentVariableRange.numberOfSteps}, "
            f"selections = {['time'] + self.outputVariables})\n"
        )
        # Convert to pandas dataframe
        code += f"{taskid} = pd.DataFrame({taskid}, columns={taskid}.colnames)\n"
        return headers, code


class Calculation(AbstractTask):
    """The definition of a 'calculation' task, which performs a calulation on inputs."""

    def __init__(self, config: dict):
        # TODO: error checking
        super().__init__(config)
        self.type_key = "calculation"
        self.math = config.pop("math", None)
        self.units = config.pop("units", None)
        self.__validate(config)
        # self.visitor = default_math_visitor()
        # self.expression = visit_expression(self.math, self.visitor)

    def __str__(self):
        ret = f"Calculation object.  Infix: '{self.math}'\n"
        if self.units:
            ret += f"Units: '{self.units}'\n"
        return ret.strip()

    def __repr__(self):
        return self.__str__()

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Calculation:", leftovers)
            return True
        return False

    def getInputVariables(self):
        """Parse the infix to retrieve all SED variable inputs."""
        strlist = re.findall(r"#[a-zA-Z0-9_:.]*", self.math)
        return set(strlist)

    def exportToPython(self, key, root_dir):
        headers = set()
        line = str_to_py_str(self.math)
        line = line.replace("^", "**")
        code = f"{str_to_py_str(key)} = {line}\n"
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
        super().__init__(config)
        self.type_key = "sumOfSquares"
        self.inputs = config.pop("inputs", None)
        self.__validate(config)

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating SumOfSquares:", leftovers)
            return True
        return False

    def exportToPython(self, key, root_dir):
        headers = set()
        code = ""
        return headers, code


class ParameterScan(AbstractTask):
    """The definition of a 'parameter scan' task, which takes a model as input and outputs an array of models."""

    def __init__(self, config: dict):
        self.type_key = "parameterScan"
        super().__init__(config)
        self.model = config.pop("model", None)
        self.scannedVariable = config.pop("scannedVariable", None)
        self.range = Range(config.pop("range", {}))
        self.outputRange = config.pop("outputRange", None)
        self.__validate(config)

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating ParameterScan:", leftovers)
            return True
        return False

    def exportToPython(self, key, root_dir):
        headers = set()
        code = ""
        return headers, code


class SteadyState(AbstractTask):
    """The definition of a 'parameter scan' task, which takes a model as input and outputs an array of models."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.type_key = "steadyState"
        self.model = config.pop("model", None)
        self.outputVariables = config.pop("outputVariables", None)
        self.outputModel = config.pop("outputModel", None)
        self.__validate(config)

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating SteadyState:", leftovers)
            return True
        return False

    def exportToProcessBigraph():
        """foo"""
        pass

    def exportToPython(self, key, root_dir):
        headers = set()
        code = ""
        return headers, code


class Loop(AbstractTask):
    """The definition of a 'loop' task, which takes a model as input and outputs an array of models."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.type_key = "loop"
        self.outputVariables = config.pop("outputVariables", None)
        self.range = Range(config.pop("range", {}))
        self.loopVariables = {}
        loopVariables = config.pop("loopVariables", {})
        if loopVariables:
            for key, config in loopVariables.items():
                self.loopVariables[key] = LoopVariable(config)
        aggregateOutputs = config.pop("aggregateOutputs", {})
        if aggregateOutputs:
            for key, config in aggregateOutputs.items():
                self.aggregateOutputs[key] = AggregationCalculation(config)
        subTasks = load_tasks_section(config.pop("subTasks", {}))
        self.__validate(config)

    def __validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating SteadyState:", leftovers)
            return True
        return False

    def exportToProcessBigraph():
        """foo"""
        pass

    def exportToPython(self, key, root_dir):
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
            case "boundedODESimulation":
                tasks[key] = BoundedODESimulation(config)
            case "explicitStochasticSimulation":
                tasks[key] = ExplicitStochasticSimulation(config)
            case "calculation":
                tasks[key] = Calculation(config)
            case "sumOfSquares":
                tasks[key] = SumOfSquares(config)
            case "parameterScan":
                tasks[key] = ParameterScan(config)
            case "steadyState":
                tasks[key] = SteadyState(config)
            case None:
                raise ValueError(f"No '_type' provided for task {key}.")
            case _:
                print(f"unknown task type: {step_type}")
                # raise ValueError(f"Unknown task type {step_type}.")
    return tasks
