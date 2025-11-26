import typing

import numpy as np
from numpy.typing import NDArray
from process_bigraph import Step

# ruff: noqa: TRY003


def mean_squared_error_dict(a: dict[str, NDArray[np.float64]], b: dict[str, NDArray[np.float64]]) -> float:
    sum_sq = 0.0
    count = 0

    common_keys = set(a.keys()) & set(b.keys())
    if not common_keys:
        raise ValueError("No overlapping keys between result dictionaries")

    for key in common_keys:
        va = a[key]
        vb = b[key]
        if len(va) != len(vb):
            raise ValueError(f"Length mismatch for key '{key}': {len(va)} vs {len(vb)}")
        for xa, xb in zip(va, vb):
            diff = xa - xb
            sum_sq += diff * diff
            count += 1

    if count == 0:
        raise ValueError("No data points to compare (count == 0)")

    return sum_sq / count


def independent_mean_squared_error(a: list[float], b: list[float]) -> float:
    sum_sq = 0.0
    count = 0
    if len(a) != len(b) or len(a) == 0 or len(b) == 0:
        raise ValueError(f"Length mismatch for key 'a':{len(a)}  and 'b': {len(b)}")
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
