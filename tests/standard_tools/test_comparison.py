import pytest
from process_bigraph import Composite
import math


def test_mse_comparison(comparison_composite: Composite):
    comparison_result = comparison_composite.bridge_updates[-1]['result']['species_mse']
    for k in comparison_result.keys():
        for compared_to in comparison_result[k]:
            if compared_to == k:
                assert comparison_result[k][compared_to] == 0
            else:
                assert comparison_result[k][compared_to] < 1e-6
                assert comparison_result[k][compared_to] != 0


