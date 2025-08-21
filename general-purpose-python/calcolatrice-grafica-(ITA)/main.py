import random
import time
import os


print("\n\n----- BLACKJACK -----\n\nNB. non si incentiva in nessun modo il gioco d'azzardo, questo è solo un esempio di elaborato")

def clear():
  print("\n"*3)
  print("---------")
  print("\n"*3)
    
def mostra(utente, banco, prima_coperta):
    carte_banco = ""
    carte_utente = ""
    for i in range(0,len(banco)):
        if prima_coperta and i == 0:
            carte_banco += "| X "
        elif i != 0 or not prima_coperta:
            carte_banco += f"| {banco[i]} "
    carte_banco += "|"
    for i in utente:
        carte_utente += f"| {i} "
    carte_utente += "|"
    print(carte_banco)
    print(max(len(banco), len(utente))*"-----")
    print(carte_utente)
    print("\n"*2)

k = 0

while True:
  k += 1
  clear()
  print(f"Partita {k}")
  mazzo_utente = []
  mazzo_banco = []
  punti = 0
  punti_banco = 0
  carte = ["A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2"]
  valori = {
      
      "A":11,
      "K":10,
      "Q":10,
      "J":10,
      "10":10,
      "9":9,
      "8":8,
      "7":7,
      "6":6,
      "5":5,
      "4":4,
      "3":3,
      "2":2
  }

  for i in range(0,2):
      rand = random.randint(0,len(carte)-1)
      mazzo_utente.append(carte[rand])
      
  for i in range(0,2):
      rand = random.randint(0,len(carte)-1)
      mazzo_banco.append(carte[rand])

  onceu = True
  onceb = True

  while True:
      clear()
      mostra(mazzo_utente, mazzo_banco, True)
      punti = 0
      punti_banco = 0
      for carta in mazzo_utente:
              punti += valori[carta]
              if punti > 21 and "A" in mazzo_utente and onceu:
                  punti = punti - (10*mazzo_utente.count("A"))
                  onceu = False
      for carta in mazzo_banco:
              punti_banco += valori[carta]
              if punti_banco > 21 and "A" in mazzo_banco and onceb:
                  punti_banco = punti_banco - (10*mazzo_banco.count("A"))
                  onceb = False
      
      if punti <= 21:
          print(f"Hai {punti} punti")
          scelta = input("\nPesca / Ferma (P/F): ")
          if scelta.strip().capitalize() == "P":
              rand = random.randint(0,len(carte)-1)
              mazzo_utente.append(carte[rand])
          elif scelta.strip().capitalize() == "F":
              mostra(mazzo_utente, mazzo_banco, False)
              while punti_banco < 17:
                  time.sleep(1)
                  rand = random.randint(0,len(carte)-1)
                  mazzo_banco.append(carte[rand])
                  punti_banco = 0
                  for carta in mazzo_banco:
                      punti_banco += valori[carta]
                      if punti_banco > 21 and "A" in mazzo_banco and onceb:
                          punti_banco = punti_banco - (10*mazzo_banco.count("A"))
                          onceb = False
                  clear()
                  mostra(mazzo_utente, mazzo_banco, False)
                          
                  
              if punti_banco > 21 or punti_banco < punti:
                  print("Hai vinto!")
                  if "A" in mazzo_banco:
                      print(f"{punti} contro {punti_banco-(mazzo_banco.count('A')*10)} (asso 1)\n")
                  else:
                      print(f"{punti} contro {punti_banco}\n")
                  input()
                  break
              elif punti_banco == punti:
                  print("Pareggio!")
                  print(f"{punti_banco} contro {punti}")
                  input()
                  break
              elif punti_banco > punti and punti_banco <= 21:
                  print("Hai perso!")
                  print(f"{punti_banco} contro {punti}")
                  input()
                  break
              
          
      elif punti > 21:
          print("Hai sballato!")
          if "A" in mazzo_utente:
              print(f"{punti-(mazzo_banco.count('A')*10)} (asso 1)\n")
          else:
              print(f"{punti}\n")
          input()
          break
      
      
      
      
      

