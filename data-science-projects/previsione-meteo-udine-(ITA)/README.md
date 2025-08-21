# Previsione Intensità Giornata: Modello ML Multi-Classe

Questo progetto utilizza modelli di Machine Learning supervisionato per prevedere l'intensità di una giornata in una delle seguenti 4 classi:

- Nulla o Pochissima ⚪  
- Leggera 🟢  
- Media 🟠  
- Forte 🔴  

Vengono impiegati due modelli:
- **Modello base** (Logistic Regression)
- **Modello bilanciato** (con classi riequilibrate tramite `RandomOverSampler`)

## 📊 Dataset

Il dataset include input giornalieri (numerici e categoriali) che descrivono il contesto della giornata (es. mm di Pioggia, Temperatura Media, Umidità Massima, Vento, ...). Le variabili categoriali vengono codificate tramite `OneHotEncoder`.

---

## 🧠 Modelli e Strategia

- **Classificazione multi-classe** (4 classi)
- Utilizzo di `LogisticRegression` con e senza `resampling`
- Calcolo di:
  - Confidenza della previsione (`predict_proba`)
  - Accuratezza storica per classe (estratta dalla matrice di confusione)
- Decisione finale basata su:
  - Concordanza tra i due modelli
  - Accuratezza storica della classe predetta
  - Confidenza del modello

---

## 📦 Funzionalità

- `final_model_predict(input_df)`:
  - Restituisce previsione finale, confidenza e accuratezza storica
  - Valuta entrambi i modelli
- Supporto per salvataggio e caricamento dei modelli (`.pkl`)
- Standardizzazione opzionale per migliorare le performance del modello

---

## 📈 Metriche

- Accuratezza totale
- Recall per classe (accuratezza storica per ogni intensità)
- Matrice di confusione (normalizzata)
- Confidenza della previsione