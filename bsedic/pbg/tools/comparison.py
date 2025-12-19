import typing
from typing import Any

import numpy as np
from numpy.typing import NDArray
from process_bigraph import Step

from bsedic.pbif.tools.stats import mean_squared_error_dict


class ComparisonTool(Step):
    config_schema: typing.ClassVar[dict[str, str]] = {
        "ignore_nans": "boolean",
        "columns_of_interest": "list[string]",
    }

    def inputs(self) -> dict[str, str]:
        return {
            "results": "numeric_results",
        }

    def outputs(self) -> dict[str, str]:
        return {"comparison_result": "map[map[map[float]]]"}


# class SubtractComparison(ComparisonTool):
#     def update(self, state, interval=None):
#         left = state['left']
#         right = state['right']
#         result = np.array(left) - np.array(right)
#         return {"comparison_result": result.tolist()}


class MSEComparison(ComparisonTool):
    def update(self, state: dict[str, Any], interval: Any = None) -> dict[str, Any]:
        results_map = state.get("results", {})
        if not isinstance(results_map, dict) or len(results_map) < 2:
            err_msg = "CompareResults.update expects inputs['results'] to be a dict with at least two entries."
            raise ValueError(err_msg)
        engine_ids = list(results_map.keys())

        # Extract species time-series per engine
        engine_to_species: dict[str, dict[str, NDArray[np.float64]]] = {}
        for eid in engine_ids:
            column_to_row = {}
            engines_results = results_map[eid]
            np_array = np.asarray(engines_results.get("values"))
            for i, c in enumerate(engines_results.get("columns")):
                column_to_row[c] = np_array[:, i]
            engine_to_species[eid] = column_to_row

        # Initialize symmetric MSE matrix
        species_mse = {i: dict.fromkeys(engine_ids) for i in engine_ids}

        # Matrix of each tool subtracted from the other
        # Pairwise MSE computation
        for i_idx, i_name in enumerate(engine_ids):
            for j_idx, j_name in enumerate(engine_ids):
                if i_name == j_name:
                    species_mse[i_name][j_name] = 0.0
                    continue
                # Only compute once per pair (i < j)
                if j_idx <= i_idx:
                    continue
                try:
                    mse = mean_squared_error_dict(engine_to_species[i_name], engine_to_species[j_name])
                except ValueError:
                    mse = None
                species_mse[i_name][j_name] = mse
                species_mse[j_name][i_name] = mse

        return {"comparison_result": {"species_mse": species_mse}}
