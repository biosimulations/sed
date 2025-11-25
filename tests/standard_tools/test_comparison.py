from process_bigraph import Composite


def test_mse_comparison(comparison_composite: Composite):
    comparison_result = comparison_composite.bridge_updates[-1]["result"]["species_mse"]
    for k, _v in comparison_result:
        for compared_to in comparison_result[k]:
            if compared_to == k:
                assert comparison_result[k][compared_to] == 0
            else:
                assert comparison_result[k][compared_to] < 1e-6
                assert comparison_result[k][compared_to] != 0
