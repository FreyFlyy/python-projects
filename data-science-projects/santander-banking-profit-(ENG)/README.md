# Santander Transaction Prediction — End-to-End ML Pipeline

This project implements a full **Data Science and Machine Learning workflow** applied to the **prediction of a bank transaction** based on **200 anonymous features**.  
The goal is to optimize a **business KPI**, being *total business profit*, defined as:

$\text{Profit} = \text{30€} \times \text{TP} - \text{5€} \times \text{FP}$

---

## 🚀 Key Results

- **Best model:** Large Neural Network (input → 512 → 256 → 128 → 64 → output)
- **Test-set profit (40k samples):** > €60,000  
- **Per-customer benefit:** +€1.50  
- **Estimated real-world value:** > €90,000,000 per year  

---

## 📁 Repository Structure

- `notebook.ipynb` — main notebook detailing the full analysis and modeling process  
- `executive_report.pdf` — concise summary of project and business insights  
- `requirements.txt` — Python dependencies for reproducing the workflow  
- `models/` — contains:
  - `model.pth` — final trained model parameters (`state_dict()`)  
  - `scaler.pkl` — fitted StandardScaler for preprocessing  
- `README.md` — this file

---

## ⚠️ Important Disclaimer

This project is:

- **Not affiliated** with Banco Santander or any of its subsidiaries.  
- **Not intended for commercial deployment**.  
- Built **exclusively for educational and portfolio purposes**.  
- Based on a **public Kaggle dataset** with anonymized features.  
- Not representative of real Santander operations, models, or internal data.  

Any reference to *monetary value*, *profit*, or *impact estimates* is **hypothetical**, serving only to demonstrate how a Data Scientist evaluates **business KPIs** within a modeling exercise.

---

## 🧩 Final Notes

This project is **fully reproducible** and aims to show:
- technical competence  
- modeling intuition  
- software design maturity  
- the ability to justify modeling decisions  

It is not intended to replicate any real Santander system, and all numbers are purely for **demonstrative, non-commercial** purposes

---

## 📄 License
MIT

---

## 👨‍💻 Author

Francesco Scolz

*   [Linkedin](https://www.linkedin.com/in/francesco-scolz/)
*   [GitHub](https://github.com/freyflyy)
*   [Hugging Face](https://huggingface.co/freyflyy)
*   [Kaggle](https://www.kaggle.com/freyfly)
*   [YouTube](https://www.youtube.com/@FrascoMath)
*   [Personal website](https://taplink.cc/scolz)

--

*Scolz F.*
