from process_bigraph import Composite


def test_mse_comparison(comparison_composite: Composite):
    comparison_result = comparison_composite.bridge_updates[-1]["result"]["species_mse"]
    for key in comparison_result:
        for compared_to in comparison_result[key]:
            if compared_to == key:
                assert comparison_result[key][compared_to] == 0
            else:
                assert comparison_result[key][compared_to] < 1e-6
                assert comparison_result[key][compared_to] != 0
