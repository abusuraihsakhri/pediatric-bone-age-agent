"""Regression tests for the supported descriptive bone-age computation."""
import math
import pytest
from pediatric_bone_age_agent.comparison import compare_bone_ages


@pytest.mark.parametrize("chrono,bone,expected,direction", [
    (120, 132, 12, "advanced"),
    (120, 108, -12, "delayed"),
    (120, 120, 0, "equal"),
    (0, 0, 0, "equal"),
    (240, 240, 0, "equal"),
    (120.25, 120.5, .25, "advanced"),
])
def test_comparison(chrono, bone, expected, direction):
    output = compare_bone_ages(chrono, bone, "Greulich-Pyle")
    assert output["difference_months"] == expected
    assert output["direction"] == direction
    assert output["assessment_method"] == "Greulich-Pyle"


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), -1, 241, True, "12", None])
def test_invalid_values(invalid):
    with pytest.raises(ValueError):
        compare_bone_ages(invalid, 120)
    with pytest.raises(ValueError):
        compare_bone_ages(120, invalid)


def test_invalid_method():
    with pytest.raises(ValueError):
        compare_bone_ages(120, 120, "fabricated")
