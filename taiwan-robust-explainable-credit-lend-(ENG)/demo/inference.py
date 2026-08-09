"""
Single preprocessing pipeline, used by both live prediction and the report
generator. If one pipeline diverges from the other, the results shown in the
UI and those in the PDF can drift: that is why every transformation goes through here.
"""

import numpy as np
import pandas as pd

from config import (
    NUMERIC_AND_ORDINAL,
    PAID_TO_REMAINING_CLIP_UPPER,
    CREDIT_UTIL_MEAN_CLIP_UPPER,
    CREDIT_UTIL_TREND_CLIP_LOWER,
    CREDIT_UTIL_TREND_CLIP_UPPER,
    PI_TRAIN,
    PI_REAL,
)
from model_registry import ModelRegistry


def calibrate_probabilities(p_raw, pi_train=PI_TRAIN, pi_real=PI_REAL):
    """Calibrate raw probabilities to account for class imbalance between training and real-world distributions (Saerens et al. 2002)."""
    p_raw = np.asarray(p_raw, dtype=float)
    w_pos = pi_real / pi_train
    w_neg = (1 - pi_real) / (1 - pi_train)
    numerator = p_raw * w_pos
    denominator = numerator + (1 - p_raw) * w_neg
    return numerator / denominator


def impute_missing(raw_input: dict, missing_features: list, registry: ModelRegistry) -> dict:
    """Replaces missing values with the cached train-set median. Does not modify the original input."""
    imputed = dict(raw_input)
    for feature in missing_features:
        imputed[feature] = registry.get_median(feature)
    return imputed


def prepare_input(
    raw_input: dict,
    customer_id,
    registry: ModelRegistry,
    missing_features: list | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Applies, in order, for ANY model (uniform):
      1. median imputation (only if missing_features is provided)
      2. clipping (PAID_TO_REMAINING_*, CREDIT_UTIL_MEAN, CREDIT_UTIL_TREND, PAY_AMT* at 99th percentile)
      3. scaling via shared preprocessor

    Returns (X_scaled, X_unengineered) where X_unengineered is the version
    post-imputation but pre-clipping/scaling, used for readability in the report.
    """
    if missing_features:
        raw_input = impute_missing(raw_input, missing_features, registry)

    X_input = pd.DataFrame([raw_input])
    X_input.index = [customer_id]
    X_input = X_input[NUMERIC_AND_ORDINAL]  # enforce column order

    X_unengineered = X_input.copy()

    # Clipping (uniform for all models)
    for col in [c for c in X_input.columns if c.startswith("PAID_TO_REMAINING_")]:
        X_input[col] = X_input[col].clip(upper=PAID_TO_REMAINING_CLIP_UPPER)

    X_input["CREDIT_UTIL_MEAN"] = X_input["CREDIT_UTIL_MEAN"].clip(upper=CREDIT_UTIL_MEAN_CLIP_UPPER)
    X_input["CREDIT_UTIL_TREND"] = X_input["CREDIT_UTIL_TREND"].clip(
        lower=CREDIT_UTIL_TREND_CLIP_LOWER, upper=CREDIT_UTIL_TREND_CLIP_UPPER
    )

    for col in [c for c in X_input.columns if "PAY_AMT" in c]:
        if col in registry.pay_amt_thresholds:
            X_input[col] = X_input[col].clip(upper=registry.pay_amt_thresholds[col])

    # Scaling (uniform for all models, as required)
    X_scaled = pd.DataFrame(
        registry.preprocessor.transform(X_input),
        columns=NUMERIC_AND_ORDINAL,
        index=X_input.index,
    )

    return X_scaled, X_unengineered


def predict_proba(X_scaled: pd.DataFrame, model_name: str, registry: ModelRegistry) -> float:
    """Returns the calibrated default probability (positive class) for a single customer."""
    model = registry.get_model(model_name)
    proba_raw = model.predict_proba(X_scaled)
    p_raw = float(proba_raw[0][1])
    return float(calibrate_probabilities(p_raw))


def classify_proba(proba: float, model_name: str, registry: ModelRegistry) -> str:
    """Binary label based on the model-specific decision threshold."""
    threshold = registry.get_decision_threshold(model_name)
    return "Default" if proba >= threshold else "Non default"
