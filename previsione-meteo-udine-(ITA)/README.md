# Predittore di Precipitazione nella Città di Udine (S. Osvaldo)

## 📝 Panoramica del Progetto

Questo programma professionale è un modello di Machine Learning ideato per predire la situazione di pioggia del giorno successivo, basandosi sui dati meteorologici registrati nel giorno attuale nella città di Udine (S. Osvaldo).

Il progetto è stato sviluppato per servire come un buon punto di partenza per modellazioni meteorologiche su dataset pubblici. Si è privilegiato l'equilibrio tra la previsione di giornate di pioggia e giornate non piovose, piuttosto che puntare alla sola accuratezza massima.

## ⚙️ Modello e Metodologia

Il modello utilizzato è un **RandomForestClassifier** di tipo *ensemble*, proveniente dalla libreria `scikit-learn`.

Per la preparazione dei dati, sono state adottate le seguenti fasi:

1.  **Importazione Dati:** Il notebook importa il file `Udine_dati_meteo.parquet`, reperibili pubblicamente dal sito dell'ArpaFVG.
2.  **Pulizia e Trasformazione:** I valori vuoti nelle colonne numeriche sono riempiti utilizzando il `SimpleImputer` (strategia "mean"), e le variabili categoriche sono convertite in un formato leggibile dal modello tramite `OneHotEncoding`. Non è stata applicata la standardizzazione dei dati, poiché i modelli ad albero (come il RandomForest) non ne necessitano.
3.  **Divisione Dati:** I dati sono stati divisi in un set di training (80% del totale) e un set di test (20% del totale).
4.  **Bilanciamento delle Classi:** Per affrontare lo sbilanciamento dei casi di training (dove i "Casi di giornata limpida" sono 2469 e i "Casi di pioggia" sono 1018), sono stati specificati pesi diversi per le classi "Nulla o Minima" e "Presente". I parametri ottimizzati (compromesso tra semplicità e interpretabilità) sono stati `max_depth = 2` e un coefficiente di riequilibrio (`factor`) pari a 1.0327.

## 📊 Variabili di Input e Output

Il modello utilizza i seguenti parametri raccolti dal giorno attuale per formulare la previsione [1]:

| Categoria | Variabili di Input | Unità di Misura/Formato |
| :--- | :--- | :--- |
| **Pioggia** | mm di Pioggia di oggi | mm |
| **Temperatura** | Massima, Minima, Media | Gradi Celsius |
| **Umidità** | Massima, Media | Percentuale (%) |
| **Tempo/Data** | Anno, Mese, Giorno (come posizione nel mese) | Stringa |
| **Vento** | Massimo, Medio, Direzione | km/h |
| **Irradiamento** | Irradiamento solare | KJ/m2 |
| **Pressione** | Pressione atmosferica media | Pascal |

**Output di Predizione:**

L'output è una stringa che definisce la situazione di pioggia del giorno successivo:

*   **"Nulla o Minima":** Se la pioggia prevista è inferiore o uguale a 0.6 mm/giorno.
*   **"Presente":** Se la pioggia prevista è superiore a 0.6 mm/giorno.

*(Nota: La soglia di 0.6 mm è stata scelta per mitigare il rumore casuale di misurazione).*

## 📈 Performance e Metriche

L'accuratezza del modello è stata valutata sul set di test:

| Metrica | Risultato (%) |
| :--- | :--- |
| **Accuratezza Totale** | 71.35% |
| **Recall (Nulla o Minima)** | 71.28% |
| **Recall (Presente)** | 71.5% |
| **ROC-AUC score** | 77.27% |
| **Precisione totale** | 52.4% |
| **F1 score** | 60.47% |

In sintesi, il modello è in grado di prevedere correttamente circa il 71.35% dei casi sul set di dati storici.

## ✍️ Autore e Contatti
Francesco Scolz

*   [Linkedin](https://www.linkedin.com/in/francesco-scolz/)
*   [GitHub](https://github.com/freyflyy)
*   [Hugging Face](https://huggingface.co/freyflyy)

## ⚖️ Licenza

MIT