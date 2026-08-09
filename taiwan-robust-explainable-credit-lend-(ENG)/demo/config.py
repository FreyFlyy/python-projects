"""
Centralized configuration: file paths and feature definitions.
No logic here, only constants.
"""

# --- Feature list (binding order, must match the preprocessor fitted during training) ---
NUMERIC_AND_ORDINAL = [
    'LIMIT_BAL',
    'PAY_SEP', 'PAY_AUG', 'PAY_JUL', 'PAY_JUN', 'PAY_MAY', 'PAY_APR',
    'PAY_AMTSEP', 'PAY_AMTAUG', 'PAY_AMTJUL', 'PAY_AMTJUN', 'PAY_AMTMAY', 'PAY_AMTAPR',
    'PAID_TO_REMAINING_SEP', 'PAID_TO_REMAINING_AUG', 'PAID_TO_REMAINING_JUL',
    'PAID_TO_REMAINING_JUN', 'PAID_TO_REMAINING_MAY', 'PAID_TO_REMAINING_APR',
    'CREDIT_UTIL_MEAN', 'CREDIT_UTIL_TREND'
]

# --- Model paths ---
MODEL_PATHS = {
    "LR": "./models/final/LR.joblib",
    "RF": "./models/final/RF.joblib",
}

PREPROCESSOR_PATH = "./models/final/preprocessor.joblib"
DECISION_THRESHOLDS_PATH = "./models/final/decision_thresholds.joblib"
PAY_AMT_THRESHOLDS_PATH = "./models/final/pay_amt_99th.joblib"
EXPLAINERS_PATH = "./tests/shap_analysis/explainers.pkl"

# --- Data paths for imputation ---
TRAIN_RAW_PATH = "./data/splits/raw/train_input_raw.csv"

# --- Report output path ---
REPORT_OUTPUT_DIR = "./tests/shap_analysis/local_patients"

# --- Scenario -> default model map (used only when there are NO missing values) ---
SCENARIO_TO_MODEL = {
    "Realistic / day-to-day": "RF",
    "Noisy / Highly uncertain": "LR",
}

# --- Missing-data fallback policy ---
# If n_missing <  MISSING_FEATURES_FALLBACK_THRESHOLD -> use the scenario-selected model.
# If n_missing >= MISSING_FEATURES_FALLBACK_THRESHOLD -> force FAILSAFE_MODEL.
MISSING_FEATURES_FALLBACK_THRESHOLD = 6
FAILSAFE_MODEL = "LR"

# --- Feature grouping by nature, only for UI layout (processing order remains NUMERIC_AND_ORDINAL) ---
FEATURE_GROUPS = {
    "Credit & Utilization": ["LIMIT_BAL", "CREDIT_UTIL_MEAN", "CREDIT_UTIL_TREND"],
    "Payment Delay (in Months)": ["PAY_SEP", "PAY_AUG", "PAY_JUL", "PAY_JUN", "PAY_MAY", "PAY_APR"],
    "Payment Amounts (in $)": ["PAY_AMTSEP", "PAY_AMTAUG", "PAY_AMTJUL", "PAY_AMTJUN", "PAY_AMTMAY", "PAY_AMTAPR"],
    "Paid-to-Remaining Ratio (paid/bill)": [
        "PAID_TO_REMAINING_SEP", "PAID_TO_REMAINING_AUG", "PAID_TO_REMAINING_JUL",
        "PAID_TO_REMAINING_JUN", "PAID_TO_REMAINING_MAY", "PAID_TO_REMAINING_APR",
    ],
}

# --- Columns subject to clipping ---
PAID_TO_REMAINING_CLIP_UPPER = 2.0
CREDIT_UTIL_MEAN_CLIP_UPPER = 1.5
CREDIT_UTIL_TREND_CLIP_LOWER = -0.3
CREDIT_UTIL_TREND_CLIP_UPPER = 0.3

# --- Calibration constants (Saerens et al. 2002) ---
# Training prior from UCI Taiwan dataset, real-world prior from production estimate
PI_TRAIN = 0.2213
PI_REAL = 0.003
