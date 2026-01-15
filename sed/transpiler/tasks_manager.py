class Range(object):
    """A 'range' object, used whenever  actor to execute simulations."""

    def __init__(self, range_config: dict):
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
        self.model = utc_config.pop("model", None)
        self.timeRange = Range(utc_config.pop("timeRange", {}))
        self.outputVariables = utc_config.pop("outputVariables", None)
        self.initialTime = utc_config.pop("initialTime", None)
        self.validate(utc_config)
    
    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating UniformTimeCourse:", leftovers)
            return True
        return False


class Calculation(object):
    """The definition of a 'calculation' task, which performs a calulation on inputs."""
    
    def __init__(self, calc_config: dict):
        #TODO: error checking
        self.infix = calc_config.pop("math", None)
        self.units = calc_config.pop("units", None)
        self.validate(calc_config)
    
    def __str__(self):
        ret = "Infix: '" + self.infix + "'\n"
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
        print("Not actually doing anything yet.")
        return []


class SumOfSquares(object):
    """The definition of a 'sumOfSquares' task, which calculates the differences between inputs."""
    
    def __init__(self, sos_config: dict):
        self.inputs = sos_config.pop("inputs", None)
        self.validate(sos_config)
    
    def validate(self, leftovers={}):
        """Validate."""
        if len(leftovers):
            print("Unsaved data when creating SumOfSquares:", leftovers)
            return True
        return False


class ParameterScan(object):
    """The definition of a 'parameter scan' task, which takes a model as input and outputs an array of models."""
    
    def __init__(self, paramscan_config: dict):
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


class SteadyState(object):
    """The definition of a 'parameter scan' task, which takes a model as input and outputs an array of models."""
    
    def __init__(self, ss_config: dict):
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
            
        # step_config = {
        #     "_type": "step",
        #     "address": f"local:{step_type}",
        #     "config": {},
        #     "inputs": make_inputs(step_type, config),
        #     "_outputs": make_outputs(step_type, outputs),
        #     "outputs": {output_key: [key, output_key] for output_key in outputs},
        # }


    return tasks


