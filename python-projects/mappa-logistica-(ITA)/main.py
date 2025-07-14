###importazioni
import matplotlib.pyplot as plt

###inizializzazione
try:
  print("Funzione logistica")
  #variabili
  r = float(input("\n\n-----------\n\n\nValore r (generalmente tra 1.1 e 3.5): "))
  n = float(input("Valore n iniziale (tra 0 e 1, non compresi): "))
  cicli = int(input("Cicli(x): "))
  #controlla variabili valide
  if r > 0 and n < 1 and n > 0 and cicli > 0:
    x = [i for i in range(0,cicli+1)]
    y = []
    
    #creazione funzione dai dati
    y.append(r*n*(1-n))
    for j in range(1,cicli+1):
      y.append(r*y[len(y)-1]*(1-y[len(y)-1]))
    #info aggiuntive
    print("\n\n-----------\n\nPer sapere di più sulla funzione logistica:\nwww.youtube.com/watch?v=ovJcsL7vyrk")
    
    #mostra grafico
    plt.plot(x, y)
    plt.show()
  else:
    ###errore dati
    print("Dati invalidi, riavviare il programma")
except:
  ###errore dati
  print("Dati invalidi, riavviare il programma")
