# Financial Price Prediction with Machine Learning

This project explores the problem of **predicting the daily price variation of Bitcoin (BTC-USD)** using a combination of **technical indicators** and **temporal features**.

---

We focused on:
- **RSI (14 days)**
- **Standard Deviation (14 days)**
- **Previous day’s closing price**
- **Temporal features**: month, day of the week, year

The target variable is defined as the **daily price variation**:  
\[
\Delta Price = Price_{t} - Price_{t-1}
\]

---

## 📊 Data
- Source: **Yahoo Finance (BTC-USD)**
- Time range: 2015 - 2025 (~3650 records)
- Processed with:
  - `pandas`, `numpy` for preprocessing
  - `pytorch` for modeling

---

## ⚙️ Methodology
1. **Data Cleaning & Feature Engineering**
   - Extracted temporal features from the `Date` column
   - Calculated **RSI (14 days)** and **STD (14 days)**
   - Standardized all numerical features

2. **Exploratory Data Analysis (EDA)**
   - Checked distributions and correlations

3. **Modeling**
   - Implemented: **Neural Networks (MLP)** – from basic to complex architectures
   - Loss function: **MSELoss**
   - Optimizer: **Adam** (lr = 0.001)

4. **Evaluation**
   - Compared models via:
     - Training/validation losses
     - Distribution (KDE) of predictions
     - Prediction vs. actual plots

---

## 🔍 Results & Findings
- All models produced **predictions concentrated around the mean/median**, with **low variance**.
- Increasing model complexity (e.g., deeper MLPs) did not significantly improve performance.

---

## 🚀 Conclusions & Next Steps
This study shows that with the chosen feature set, **predicting short-term BTC price movements is not feasible with high confidence**.

Future improvements could include:
- Expanding the feature set (e.g., longer RSI/STD windows, moving averages, macroeconomic indicators)
- Predicting **multi-day aggregated movements** instead of daily deltas
- Reformulating the problem as **classification** (e.g., up vs. down) instead of regression
- Exploring **alternative targets** (e.g., volatility, trend direction)

---

## 📖 License

This project is released under the MIT License.