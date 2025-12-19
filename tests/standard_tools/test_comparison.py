from typing import Any

from process_bigraph import Composite, ProcessTypes


def test_mse_comparison(comparison_document: dict[Any, Any], fully_registered_core: ProcessTypes) -> None:
    comparison_composite = Composite(config=comparison_document, core=fully_registered_core)
    comparison_result = comparison_composite.bridge_updates[-1]["result"]["species_mse"]
    for key in comparison_result:
        for compared_to in comparison_result[key]:
            if compared_to == key:
                assert comparison_result[key][compared_to] == 0
            else:
                assert comparison_result[key][compared_to] < 1e-6
                assert comparison_result[key][compared_to] != 0
