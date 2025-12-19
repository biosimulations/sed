import copy
from enum import Enum
from typing import Any, Optional

from process_bigraph import Composite, Process, ProcessTypes, Step


class StepBuilder(Step):
    pass


class ComparisonProcess(Process):
    pass


class CompositeOverrides:
    pass


class CompositeParameterScan:
    pass


class CompositeBuilder:
    class CompositeType(Enum):
        CONFIG = "config"
        STATE = "state"

    class _PathNavigation:
        def __init__(self, path: list[str], values: list[Any], composite_type: Any) -> None:
            self.path: list[str] = path
            self.values: list[Any] = values
            self.composite_type: CompositeBuilder.CompositeType = composite_type

    def __init__(self, core: ProcessTypes):
        self.core: ProcessTypes = core
        self.step_number: int = 0
        self.state: dict[str, Any] = {}

    def _allocate_step_key(self, step_name: str) -> str:
        step_key = f"{step_name}_{self.step_number}"
        self.step_number += 1
        return step_key

    def add_step(
        self, address: str, config: dict[str, str | int], inputs: dict[str, Any], outputs: dict[str, Any]
    ) -> None:
        new_step_key = self._allocate_step_key(address)
        self.state[new_step_key] = {
            "_type": "step",
            "address": address,
            "config": config,
            "inputs": inputs,
            "outputs": outputs,
        }

    def add_comparison_step(self, comparison_name: str, store_with_values: list[str]) -> None:
        comparison_step_key = self._allocate_step_key("comparison_step")
        self.state[comparison_step_key] = {
            "_type": "step",
            "address": "local:bsedic.pbif.tools.comparison.MSEComparison",
            "config": {},
            "inputs": {
                "results": store_with_values,
            },
            "outputs": {
                "comparison_result": ["comparison_results", comparison_name],
            },
        }

    def _deconstruct_dictionary(
        self, base_path: list[str], dict_values: dict[str, Any], composite_type: CompositeType
    ) -> list[_PathNavigation]:
        keys_of_interest = list(dict_values.keys())
        paths_to_navigate: list[CompositeBuilder._PathNavigation] = []
        for fixated_key in keys_of_interest:
            new_path = [*base_path, fixated_key]
            if type(dict_values[fixated_key]) is dict:
                paths_to_navigate += self._deconstruct_dictionary(new_path, dict_values[fixated_key], composite_type)
            elif type(dict_values[fixated_key]) is list:
                paths_to_navigate.append(self._PathNavigation(new_path, dict_values[fixated_key], composite_type))
            else:
                err_msg = (
                    f"Invalid type for combination for {dict_values} at {fixated_key}: {type(dict_values[fixated_key])}"
                )
                raise TypeError(err_msg)
        return paths_to_navigate

    def add_parameter_scan(
        self,
        step_address: str,
        step_config: dict[Any, Any],
        input_mappings: dict[str, list[str]],
        config_values: Optional[dict[str, Any]] = None,
        state_values: Optional[dict[str, Any]] = None,
    ) -> None:
        config_values = config_values or {}
        state_values = state_values or {}
        param_step_key = self._allocate_step_key("parameter_scan")
        self.state[param_step_key] = {}
        self.state[param_step_key]["results"] = {}
        self.state[param_step_key]["inputs"] = {}

        parameter_values: list[CompositeBuilder._PathNavigation] = self._deconstruct_dictionary(
            [], state_values, CompositeBuilder.CompositeType.STATE
        ) + self._deconstruct_dictionary([], config_values, CompositeBuilder.CompositeType.CONFIG)

        def combinatorics(current_step: dict, all_paths: list[CompositeBuilder._PathNavigation]) -> None:
            path_of_focus = all_paths[-1]
            for cur_value in path_of_focus.values:
                # put appropriate values
                sub_struct = None
                match path_of_focus.composite_type:
                    case CompositeBuilder.CompositeType.CONFIG:
                        sub_struct = current_step["step"]["config"]
                    case CompositeBuilder.CompositeType.STATE:
                        sub_struct = current_step["state"]

                i = 0
                while i < len(path_of_focus.path):
                    if i == len(path_of_focus.path) - 1:
                        sub_struct[path_of_focus.path[i]] = cur_value
                    elif path_of_focus.path[i] not in sub_struct:
                        sub_struct[path_of_focus.path[i]] = {}
                    sub_struct = sub_struct[path_of_focus.path[i]]
                    i += 1

                # pass down as needed
                if len(all_paths) > 1:
                    combinatorics(current_step, all_paths[:-1])
                else:
                    step_key = self._allocate_step_key(step_address.split(":")[1])
                    current_step["step"]["outputs"]["result"] = ["results", step_key]
                    for k in current_step["step"]["inputs"]:
                        current_step["step"]["inputs"][k] = ["inputs", step_key]
                    self.state[param_step_key]["inputs"][step_key] = copy.deepcopy(current_step["state"])
                    self.state[param_step_key][step_key] = copy.deepcopy(current_step["step"])

        combinatorics(
            {
                "state": {},
                "step": {
                    "_type": "step",
                    "address": step_address,
                    "config": step_config,
                    "inputs": input_mappings,
                    "outputs": {"result": {}},
                },
            },
            parameter_values,
        )

    def build(self) -> Composite:
        comp = Composite({"state": self.state}, core=self.core)
        return comp
