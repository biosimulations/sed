import typing

import numpy as np
from numpy.typing import NDArray
from process_bigraph import Step


def mean_squared_error_dict(a: dict[str, NDArray[np.float64]], b: dict[str, NDArray[np.float64]]) -> float:
    sum_sq = 0.0
    count = 0

    common_keys = set(a.keys()) & set(b.keys())
    if not common_keys:
        err_msg = "No overlapping keys between result dictionaries"
        raise ValueError(err_msg)

    for key in common_keys:
        va = a[key]
        vb = b[key]
        if len(va) != len(vb):
            err_msg = f"Length mismatch for key '{key}': {len(va)} vs {len(vb)}"
            raise ValueError()
        for xa, xb in zip(va, vb):
            diff = xa - xb
            sum_sq += diff * diff
            count += 1

    if count == 0:
        err_msg = "No data points to compare (count == 0)"
        raise ValueError(err_msg)

    return sum_sq / count


def independent_mean_squared_error(a: list[float], b: list[float]) -> float:
    sum_sq = 0.0
    count = 0
    if len(a) != len(b) or len(a) == 0 or len(b) == 0:
        err_msg = f"Length mismatch for key 'a':{len(a)}  and 'b': {len(b)}"
        raise ValueError(err_msg)
    for xa, xb in zip(a, b):
        diff = xa - xb
        sum_sq += diff * diff
        count += 1
    return sum_sq / count


class StatsTool(Step):
    config_schema: typing.ClassVar[dict[str, str]] = {
        "ignore_nans": "boolean",
    }

    def inputs(self) -> dict[str, str]:
        return {
            "compute_store": "array",
        }

    def outputs(self) -> dict[str, str]:
        return {"stats_result": "array"}


class SumOfSquaresTool(StatsTool):
    def update(self, state: dict[str, typing.Any], interval: typing.Any = None) -> dict[str, typing.Any]:
        compute_store = np.array(state["compute_store"])
        row, col = compute_store.shape
        result = np.empty((row, col))
        means = compute_store.mean(axis=0)
        for r in range(row):
            for c in range(col):
                res = (compute_store[r, c] - means[c]) ** 2
                result[r, c] = res
        return {"stats_result": result.tolist()}
