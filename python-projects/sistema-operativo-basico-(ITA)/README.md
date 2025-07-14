### FRASCO OS — Sistema Operativo Simulato ###

Un sistema operativo testuale interattivo interamente scritto in Python, con un filesystem virtuale gestito in RAM

---

## Descrizione

FRASCO OS simula un ambiente a riga di comando (tipo UNIX) in cui puoi:

- Navigare tra cartelle e sottocartelle
- Creare, leggere e modificare file `.txt`
- Visualizzare contenuti delle directory

Il tutto senza usare il disco fisico: è tutto mantenuto in sessione

---

## Funzionalità principali

- restart: ripulisce il terminale
- show: mostra i file della directory attuale
- create [nome]: crea un file con nome ed estensione personalizzata
- remove [nome]: elimina un file dato il nome (con estensione)
- rename [vecchio] [nuovo]: rinomina un file dato il nome originale e nuovo
- goto [cartella o --]: vai ad una sottocartella o torna indietro (--)
- open [nome]: Apre un file .txt
- write [nome]: Sovrascrive il testo di un file .txt (sucessivamente si inserirà il testo)

---

## Limitazioni

- Tutto il contenuto è volatile: viene perso al termine dell’esecuzione
- Nessun salvataggio su disco (intenzionale, fatto per dimostrazione)