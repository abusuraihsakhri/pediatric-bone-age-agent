"""Descriptive comparison of a manually assessed skeletal age with chronological age.

This module does not estimate bone age from radiographs, score GP/TW features,
predict final height, or apply clinical diagnostic cut-offs.
"""
import math


METHODS = ("Unspecified", "Greulich-Pyle", "Tanner-Whitehouse", "Other")


def compare_bone_ages(chronological_age_months, bone_age_months, method="Unspecified"):
    """Return a signed age difference in months (bone minus chronological)."""
    for name, value in (
        ("chronological_age_months", chronological_age_months),
        ("bone_age_months", bone_age_months),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a finite number")
        if not math.isfinite(value) or not 0 <= value <= 240:
            raise ValueError(f"{name} must be finite and between 0 and 240 months")
    if method not in METHODS:
        raise ValueError("method must be Unspecified, Greulich-Pyle, Tanner-Whitehouse, or Other")

    delta = round(float(bone_age_months) - float(chronological_age_months), 2)
    direction = "advanced" if delta > 0 else "delayed" if delta < 0 else "equal"
    return {
        "chronological_age_months": round(float(chronological_age_months), 2),
        "bone_age_months": round(float(bone_age_months), 2),
        "difference_months": delta,
        "direction": direction,
        "assessment_method": method,
        "limitations": (
            "Descriptive arithmetic only. The skeletal age must be assessed independently. "
            "No radiograph interpretation, diagnostic cut-off, or adult-height prediction is performed."
        ),
    }
