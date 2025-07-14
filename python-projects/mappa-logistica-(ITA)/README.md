# Mappa Logistica

Un programma Python che calcola e visualizza l’iterazione della funzione logistica:

x_{n+1} = r * x_n * (1 - x_n)


## Descrizione

Data la costante di crescita (r), la popolazione iniziale (n_0) e il numero di iterazioni, il programma calcola la sequenza di valori n della funzione logistica.

Per valori r:
- r < 0: la popolazione non ha senso biologico e si estingue
- 0 ≤ r < 1: la popolazione ha senso biologico ma si estingue
- 1 ≤ r < 3: la popolazione ha una popolazione di equilibrio
- 3 ≤ r < 3.57: la popolazione non ha una popolazione di equlibrio, ma ha comunque una certa regolarità
- 3.57 ≤ r < 4: la popolazione non ha una popolazione di equlibrio e non ha nessuna regolarità
- r > 4: la popolazione raggiunge valori impossibili al di fuori di 0 e 1
