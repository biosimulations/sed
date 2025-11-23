import pytest
from process_bigraph import Composite


def test_mse_comparison(comparison_composite: Composite):
    comparison_composite.run(1.0)
    comparison_composite.run(2.0)


