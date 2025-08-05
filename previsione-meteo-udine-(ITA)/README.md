# 🌦️ Previsione Meteo – Udine (S. Osvaldo)

Modello di **machine learning** per la previsione della pioggia del giorno successivo, basato su dati meteorologici reali raccolti nella zona di Udine (S. Osvaldo).

> ⚠️ Obiettivo: predire se **ci sarà pioggia** o **sarà una giornata limpida**, con un modello bilanciato tra accuratezza e affidabilità su entrambe le classi.


---


## 🔍 Descrizione del progetto

Il modello prende in input alcune informazioni meteorologiche **del giorno attuale** e stima la probabilità di pioggia per il giorno successivo.

### 📥 Input

- mm di pioggia (oggi)
- Temperature (min, med, max)
- Umidità (max, med)
- Pressione atmosferica
- Irraggiamento solare (KJ/m²)
- Vento (max, med, direzione)
- Mese, anno, fase del mese

### 📤 Output

- `"Nulla o Minima"` – ≤ 0.6 mm di pioggia
- `"Presente"` – > 0.6 mm di pioggia

> La soglia di 0.6 mm è scelta come compromesso per evitare rumore e falsi positivi/negativi.

---

## 🧠 Modello usato

- **RandomForestClassifier** con profondità limitata (`max_depth=2`)
- Class weighting calibrato con `factor = 1.0327` per compensare lo sbilanciamento delle classi
- Encoding delle variabili categoriche tramite `OneHotEncoder`
- Imputazione valori mancanti con `SimpleImputer`

---

## 📈 Metriche di performance

| Metrica        | Valore    |
|----------------|-----------|
| Accuracy       | ~71.4%    |
| ROC-AUC        | ~77.3%    |
| F1 (pioggia)   | ~60.5%    |
| Recall (Nulla) | ~71.3%    |
| Recall (Pioggia)| ~71.5%   |

> ⚠️ Il modello **non è ottimizzato per massima accuracy**, ma per **bilanciare bene entrambi i tipi di giornate**.

---

## 🧪 Come usare il modello

Puoi inserire i dati di una giornata in un dizionario come questo:

```python
input_to_predict = {
    "Anno": 2025,
    "Mese": "Ago",
    "PosizioneMese": "Meta",
    "DirVentoMax": "S",
    "TempMin [°C]": 18.2,
    "TempMed [°C]": 29.1,
    "TempMax [°C]": 33.6,
    "UmiditaMed [%]": 80,
    "UmiditaMax [%]": 91,
    "VentoMed [km/h]": 6,
    "VentoMax [km/h]": 23,
    "Radiazione [KJ/m2]": 11270,
    "Pressione [Pa]": 101635,
    "mmPioggia": 0
}
```

E chiamare:

```python
predict_single_day(input_to_predict)
```

Otterrai una previsione + confidenza basata sulle prestazioni storiche del modello per quel livello di probabilità.


---


🙋‍♂️ Autore

`Francesco Scolz`

Studente e aspirante data scientist


---


> ⚠️ Questo progetto ha uno scopo principalmente educativo e di dimostrazione tecnica. Non è pensato per sostituire modelli ufficiali di previsione meteorologica, ma dimostra come si possa lavorare con dataset pubblici, scelte progettuali ragionate, e costruire modelli personalizzati e adattabili.
