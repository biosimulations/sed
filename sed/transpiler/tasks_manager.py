import re

class Range(object):
    """A 'range' object, used to define a range in one of several ways:
        * start, end, numberOfSteps (and optional 'scale')
        * start, end, interval
        * start, numberOfSteps, interval
        * end, numberOfSteps, interval
        * values
    """

    def __init__(self, range_config: dict):
        self.type_key = "Range"
        self.start = range_config.pop("start", None)
        self.end = range_config.pop("end", None)
        self.numberOfSteps = range_config.pop("numberOfSteps", None)
        self.interval = range_config.pop("interval", None)
        self.scale = range_config.pop("scale", None)
        self.values = range_config.pop("values", None)
        self.validate(range_config)
    
    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating Range:", leftovers)
            return True
        return False

class UniformTimeCourse(object):
    """The definition of a uniform time course simulation."""
    
    def __init__(self, utc_config: dict):
        #TODO: error checking
        self.type_key = "UniformTimeCourse"
        self.model = utc_config.pop("model", None)
        self.timeRange = Range(utc_config.pop("timeRange", {}))
        self.outputVariables = utc_config.pop("outputVariables", None)
        self.initialTime = utc_config.pop("initialTime", None)
        self.validate(utc_config)
        self.executor = "Tellurium"
    
    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating UniformTimeCourse:", leftovers)
            return True
        return False
    
    def make_python(self, key):
        if (self.executor == "Tellurium"):
            return self.make_python_tellurium(key)
        elif (self.executor == "Copasi"):
            return self.make_python_copasi(key)
        else:
            raise ValueError("Unknown uniform time course executor '" + self.executor + "'")

    def make_python_tellurium(self, key):
        headers = set(["import tellurium as te"])
        modelid = self.model
        modelid = self.model[1:]
        modelid = modelid.replace(":", "_")
        taskid = "tasks_" + key
        code = taskid + "_r = te.loadSBMLModel(" + modelid + ")\n"
        code += taskid + " = " + taskid + "_r.simulate(" + str(self.timeRange.start) + ", " + str(self.timeRange.end) + ", steps=" + str(self.timeRange.numberOfSteps) + ", selections = " + str(self.outputVariables) + ")\n"
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
        headers = set(["import basico"])
        headers.add("import numpy as np")
        headers.add("from pandas import DataFrame")
        modelid = self.model
        modelid = self.model[1:]
        modelid = modelid.replace(":", "_")
        taskid = "tasks_" + key
        code = taskid + "_copasi = basico.run_time_course(start_time=" + str(self.timeRange.start) + ", duration=" + str(self.timeRange.end - self.timeRange.start) + ", intervals=" + str(self.timeRange.numberOfSteps) + ", update_model=True, use_sbml_id=True,model=basico.load_model(" + modelid + "))\n"
        code += taskid + " = {}\n"
        first = 0
        if (self.outputVariables[0] == "time"):
            first = 1
            code += taskid + "['time'] = np.array(" + taskid + "_copasi.index)\n"
        for var in self.outputVariables[first:]:
            code += taskid + "['" + var + "'] = np.array("+ taskid + "_copasi['"+ var + "'])\n"
        code += taskid + " = DataFrame(" + taskid + ")\n"
        return headers, code


class Calculation(object):
    """The definition of a 'calculation' task, which performs a calulation on inputs."""
    
    def __init__(self, calc_config: dict):
        #TODO: error checking
        self.type_key = "Calculation"
        self.infix = calc_config.pop("math", None)
        self.units = calc_config.pop("units", None)
        self.validate(calc_config)
    
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
        strlist = re.findall(r'#[a-zA-Z0-9_:.]*', self.infix)
        return set(strlist)

    def make_python(self, key):
        headers = set()
        line = self.infix.replace(":", "_")
        line = line.replace("#", "")
        line = line.replace("^", "**")
        code = "tasks_" + key + " = " + line + "\n"
        return headers, code

class SumOfSquares(object):
    """The definition of a 'sumOfSquares' task, which calculates the differences between inputs."""
    
    def __init__(self, sos_config: dict):
        self.type_key = "SumOfSquares"
        self.inputs = sos_config.pop("inputs", None)
        self.validate(sos_config)
    
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


class ParameterScan(object):
    """The definition of a 'parameter scan' task, which takes a model as input and outputs an array of models."""
    
    def __init__(self, paramscan_config: dict):
        self.type_key = "ParameterScan"
        self.model = paramscan_config.pop("model", None)
        self.scannedVariable = paramscan_config.pop("scannedVariable", None)
        self.range = Range(paramscan_config.pop("range", {}))
        self.outputRange = paramscan_config.pop("outputRange", None)
        self.validate(paramscan_config)
    
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


class SteadyState(object):
    """The definition of a 'parameter scan' task, which takes a model as input and outputs an array of models."""
    
    def __init__(self, ss_config: dict):
        self.type_key = "SteadyState"
        self.model = ss_config.pop("model", None)
        self.outputVariables = ss_config.pop("outputVariables", None)
        self.outputModel = ss_config.pop("outputModel", None)
        self.validate(ss_config)
    
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
            case "uniformTimeCourse":
                tasks[key] = UniformTimeCourse(config)
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
                raise ValueError("Unknown task type " + step_type + ".")
            
    return tasks


