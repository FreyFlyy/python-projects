"""
Decides which model to use based on the user-selected scenario and the
completeness of the entered data.

Policy (configurable via config.py):
  - n_missing <  MISSING_FEATURES_FALLBACK_THRESHOLD -> scenario-selected model.
  - n_missing >= MISSING_FEATURES_FALLBACK_THRESHOLD -> FAILSAFE_MODEL.
"""

from typing import Optional
from config import (
    SCENARIO_TO_MODEL,
    NUMERIC_AND_ORDINAL,
    MISSING_FEATURES_FALLBACK_THRESHOLD,
    FAILSAFE_MODEL,
)


def find_missing_features(raw_input: dict) -> list:
    """
    Returns the list of missing features (None, empty string, or not present in dict).
    NaN is not handled here because input comes from Gradio fields (no native NaN),
    but it is included for safety in case of programmatic input.
    """
    missing = []
    for feature in NUMERIC_AND_ORDINAL:
        value = raw_input.get(feature, None)
        if value is None or value == "":
            missing.append(feature)
            continue
        try:
            if value != value:  # NaN check without depending on numpy/pandas here
                missing.append(feature)
        except TypeError:
            pass
    return missing


def select_model(scenario: str, raw_input: dict) -> tuple[str, list, Optional[str]]:
    """
    Returns (model_name, missing_features, warning_message)

    - If missing_features >= MISSING_FEATURES_FALLBACK_THRESHOLD -> FAILSAFE_MODEL.
    - If 0 < missing_features < threshold -> use scenario-selected model (with warning).
    - Otherwise -> use scenario-selected model (no warning).
    """
    missing_features = find_missing_features(raw_input)
    n_missing = len(missing_features)

    if n_missing >= MISSING_FEATURES_FALLBACK_THRESHOLD:
        warning = (
            f"Critical: {n_missing} features missing (≥{MISSING_FEATURES_FALLBACK_THRESHOLD}), "
            f"fallback to {FAILSAFE_MODEL} with median imputation"
        )
        return FAILSAFE_MODEL, missing_features, warning

    if missing_features:
        warning = (
            f"Incomplete data ({n_missing} missing), using {SCENARIO_TO_MODEL[scenario]} "
            f"(scenario: {scenario})"
        )
        return SCENARIO_TO_MODEL[scenario], missing_features, warning

    if scenario not in SCENARIO_TO_MODEL:
        raise ValueError(f"Invalid scenario: {scenario}")

    return SCENARIO_TO_MODEL[scenario], [], None
