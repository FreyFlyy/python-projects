"""
Loads all artifacts (models, preprocessor, thresholds, explainers, train medians)
once at app startup. No other part of the code should call joblib.load or
pd.read_csv on these paths: always go through here.

NOTE ON EXPLAINERS:
The SHAP explainers loaded from EXPLAINERS_PATH were fitted in the notebook
04_Testing_and_deploying on the RAW model outputs (log-odds space):
  - RF: KernelExplainer on logit(raw_proba)
  - LR: LinearExplainer on the raw linear model
The app converts log-odds SHAP to calibrated probability SHAP via the
logodds_shap_to_probability function in report.py.
"""

import sys
import joblib
import pandas as pd
import numpy as np
from scipy.special import logit

from config import (
    MODEL_PATHS,
    PREPROCESSOR_PATH,
    DECISION_THRESHOLDS_PATH,
    PAY_AMT_THRESHOLDS_PATH,
    EXPLAINERS_PATH,
    TRAIN_RAW_PATH,
    NUMERIC_AND_ORDINAL,
)

# ---------------------------------------------------------------------------
# Monkey-patch: the RF KernelExplainer was saved from a notebook where
# rf_logit lived in __main__. We inject it back so joblib.load() can
# unpickle the SHAP objects without crashing.
#
# rf_logit wraps the raw RF model to return log-odds of the positive class
# probability, which is what KernelExplainer needs for exact additive SHAP
# in log-odds space.
# ---------------------------------------------------------------------------
_rf_model = None

def _make_rf_logit():
    """Factory: returns rf_logit bound to the loaded RF model."""
    model = _rf_model
    features = NUMERIC_AND_ORDINAL

    def rf_logit(x):
        # KernelExplainer passes numpy arrays; wrap to DataFrame to preserve feature names.
        if not isinstance(x, pd.DataFrame):
            x = pd.DataFrame(x, columns=features)
        p = model.predict_proba(x)[:, 1]
        p = np.clip(p, 1e-15, 1 - 1e-15)
        return logit(p)

    return rf_logit


class ModelRegistry:
    """Singleton-like container. Instantiate only once in app.py."""

    def __init__(self):
        self.models = {name: joblib.load(path) for name, path in MODEL_PATHS.items()}

        # Bind the loaded RF model for the monkey-patch before loading explainers
        global _rf_model
        _rf_model = self.models.get("RF")

        _main = sys.modules.get("__main__")
        if _main is not None and not hasattr(_main, "rf_logit") and _rf_model is not None:
            _main.rf_logit = _make_rf_logit()

        self.preprocessor = joblib.load(PREPROCESSOR_PATH)
        self.decision_thresholds = joblib.load(DECISION_THRESHOLDS_PATH)
        self.pay_amt_thresholds = joblib.load(PAY_AMT_THRESHOLDS_PATH)
        self.explainers = joblib.load(EXPLAINERS_PATH)

        # Cache medians for imputation, computed once from raw train data
        train_raw = pd.read_csv(TRAIN_RAW_PATH)
        missing_cols = [c for c in NUMERIC_AND_ORDINAL if c not in train_raw.columns]
        if missing_cols:
            raise ValueError(f"train_input_raw.csv is missing columns: {missing_cols}")
        self.train_medians = train_raw[NUMERIC_AND_ORDINAL].median().to_dict()

    def get_model(self, model_name: str):
        if model_name not in self.models:
            raise ValueError(f"Invalid model: {model_name}")
        return self.models[model_name]

    def get_explainer(self, model_name: str):
        if model_name not in self.explainers:
            raise ValueError(f"Missing explainer for model: {model_name}")
        # explainers.pkl stores {"LR": {"explainer": Explainer, ...}, ...}
        entry = self.explainers[model_name]
        if isinstance(entry, dict) and "explainer" in entry:
            return entry["explainer"]
        return entry

    def get_decision_threshold(self, model_name: str) -> float:
        threshold = self.decision_thresholds.get(model_name)
        if threshold is None:
            raise ValueError(f"Missing decision threshold for: {model_name}")
        return threshold

    def get_median(self, feature: str) -> float:
        if feature not in self.train_medians:
            raise ValueError(f"Median not available for feature: {feature}")
        return self.train_medians[feature]
