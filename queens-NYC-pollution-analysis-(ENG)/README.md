# NYC Air Pollution Analysis – Queens (2008–2021)

This project analyzes the **average annual air pollution** in Queens, New York, between 2005 and 2021 using public datasets and Python-based data science tools.

---

## 📊 Objective

Understand the evolution of air pollution over time through:
- Data cleaning and preprocessing
- Mean aggregation and standard deviation
- Linear regression
- Statistical measures (R², Pearson r, p-value)

---

## 🧰 Technologies & Libraries

- `pandas`
- `numpy`
- `matplotlib`
- `scikit-learn`
- `scipy`
- `datetime` (standard library)

---

## 📁 Dataset

The data was sourced from the **NYC Air Quality** dataset on Kaggle (https://www.kaggle.com/datasets/fatmanur12/new-york-air-quality)
The script filters **Annual Average** records for the **Queens** area.

---

## 📈 Methodology

1. **Filtering & Cleaning**: Extracted relevant measurements per year.
2. **Aggregation**: Averaged values for each year to reduce noise.
3. **Regression**: Performed linear regression to detect long-term trends.
4. **Statistical Validation**: Evaluated R², Pearson correlation, and p-value.
5. **Uncertainty**: Calculated standard deviation and Coefficient of Variation (CV) per year.

---

## 📉 Results Summary

- **Trend**: Clear decreasing trend in air pollution index.
- **Rate**: Approx. -0.4 units/year.
- **R²**: 0.939 → strong model fit.
- **Pearson r**: -0.969 → strong negative correlation.
- **p-value**: ~4.8e-08 → statistically significant.

⚠️ However, a **high CV (~40%)** suggests large intra-year variation in measurements, possibly due to regional variability.

---

## 🧠 Conclusion

Air quality in Queens improved steadily from 2008 to 2021.  
Further study is needed to assess measurement consistency across subregions.

---

**Francesco Scolz**  
[LinkedIn] (https://www.linkedin.com/in/francesco-scolz/) • [GitHub](https://github.com/FreyFlyy)

Kaggle Project: (https://www.kaggle.com/code/freyfly/queens-nyc-air-pollution-over-the-years-2021)
