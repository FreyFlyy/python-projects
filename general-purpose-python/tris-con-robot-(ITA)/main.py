import random
import time

###VARIABILI
giocatore = []
bot = []
inizio = 2 #random.randint(1,2)
mossa = 1

###FUNZIONI
def tabella(gioc, ai, printt):
    tab = []
    row1 = []
    row2 = []
    row3 = []
    row_1 = ""
    row_2 = ""
    row_3 = ""
    
    for posizione in range(1,10):
        if posizione not in gioc and posizione not in ai:
            tab.append(f"{posizione}")
        elif (posizione in gioc) and (posizione not in ai):
            tab.append("X")
        elif (posizione not in gioc) and (posizione in ai):
            tab.append("O")
            
    table =  tab
            
    row1 = tab[0:3]
    row2 = tab[3:6]
    row3 = tab[6:9]
    
            
    for row in range(1,4):
        for elem in range(1,4):
            if row == 1:
                if elem != 3:
                    row_1 += f"{row1[elem-1]} | "
                if elem == 3:
                    row_1 += f"{row1[elem-1]}"
            elif row == 2:
                if elem != 3:
                    row_2 += f"{row2[elem-1]} | "
                if elem == 3:
                    row_2 += f"{row2[elem-1]}"
            elif row == 3:
                if elem != 3:
                    row_3 += f"{row3[elem-1]} | "
                if elem == 3:
                    row_3 += f"{row3[elem-1]}"
        
    if printt:
        print(row_1)
        print("---------")
        print(row_2)
        print("---------")
        print(row_3)
    
    return tab
def clear():
    print("\n\n\n\n\n\n\n\n\n\n\n\n")
table = tabella(giocatore, bot, False)

###INIZIALIZZAZIONE
last = 0
print("--- Tris contro Robot ---")


###INIZIA GIOCATORE
if inizio == 1:
    vinta = False
    while True:
        ###TURNO GIOCATORE (TURNI DISPARI)
        if mossa%2 == 1:
            clear()
            print("\n\nTurno Giocatore\n\nScegli una casella(1-9)\n\n")
            tabella(giocatore, bot, True)
            if vinta:
                print("\nPARTITA FINITA\nIl robot ha vinto!")
                input()
                break
            vinta = False
            scegli = True
            
            while scegli:
                cas = int(input("\nCasella: "))
                if (cas not in giocatore) and (cas not in bot) and (cas > 0) and (cas < 10):
                   giocatore.append(cas)
                   scegli = False
                else:
                    print("Errore, casella non valida")
            table = tabella(giocatore, bot, False)
            condizioni_fine = [
        
                table[0]==table[1]==table[2],
                table[3]==table[4]==table[5],
                table[6]==table[7]==table[8],
                table[0]==table[3]==table[6],
                table[1]==table[4]==table[7],
                table[2]==table[5]==table[8],
                table[0]==table[4]==table[8],
                table[2]==table[4]==table[6]
            ]
            for condizione in condizioni_fine:
                if condizione:
                    vinta = True
                    break
            mossa += 1
        ###TURNO AI (TURNI PARI)
        if mossa%2 == 0:
            if vinta:
                clear()
                tabella(giocatore, bot, True)
                print("\n\nPARTITA FINITA\nIl giocatore ha vinto!")
                input()
                break
            clear()
            print("Turno del robot...\n\n")
            tabella(giocatore, bot, True)
            print("\n")
            time.sleep(2)
            vinta = False
            scegli = True
            
            while scegli:
                cas = random.randint(1,9)
                if (cas not in giocatore) and (cas not in bot) and (cas > 0) and (cas < 10):
                   bot.append(cas)
                   scegli = False
            table = tabella(giocatore, bot, False)
            condizioni_fine = [
        
                table[0]==table[1]==table[2],
                table[3]==table[4]==table[5],
                table[6]==table[7]==table[8],
                table[0]==table[3]==table[6],
                table[1]==table[4]==table[7],
                table[2]==table[5]==table[8],
                table[0]==table[4]==table[8],
                table[2]==table[4]==table[6]
            ]
            for condizione in condizioni_fine:
                if condizione:
                    vinta = True
                    break
            mossa += 1
        
###INIZIA AI
if inizio == 2:
    vinta = False
    while True:
        ###TURNO GIOCATORE (TURNI PARI)
        if mossa%2 == 0:
            clear()
            print("\n\nTurno Giocatore\n\nScegli una casella(1-9)\n\n")
            tabella(giocatore, bot, True)
            if vinta:
                print("\nPARTITA FINITA\nIl robot ha vinto!")
                input()
                break
            vinta = False
            scegli = True
            
            while scegli:
                cas = int(input("\nCasella: "))
                if (cas not in giocatore) and (cas not in bot) and (cas > 0) and (cas < 10):
                   giocatore.append(cas)
                   scegli = False
                else:
                    print("Errore, casella non valida")
            table = tabella(giocatore, bot, False)
            condizioni_fine = [
        
                table[0]==table[1]==table[2],
                table[3]==table[4]==table[5],
                table[6]==table[7]==table[8],
                table[0]==table[3]==table[6],
                table[1]==table[4]==table[7],
                table[2]==table[5]==table[8],
                table[0]==table[4]==table[8],
                table[2]==table[4]==table[6]
            ]
            for condizione in condizioni_fine:
                if condizione:
                    vinta = True
                    break
            mossa += 1
        ###TURNO AI (TURNI DISPARI)
        if mossa%2 == 1:
            if vinta:
                clear()
                tabella(giocatore, bot, True)
                print("\n\nPARTITA FINITA\nIl giocatore ha vinto!")
                input()
                break
            clear()
            print("Turno del robot...\n\n")
            tabella(giocatore, bot, True)
            print("\n")
            time.sleep(2)
            vinta = False
            scegli = True
            
            while scegli:
                cas = random.randint(1,9)
                if (cas not in giocatore) and (cas not in bot) and (cas > 0) and (cas < 10):
                   bot.append(cas)
                   scegli = False
            table = tabella(giocatore, bot, False)
            condizioni_fine = [
        
                table[0]==table[1]==table[2],
                table[3]==table[4]==table[5],
                table[6]==table[7]==table[8],
                table[0]==table[3]==table[6],
                table[1]==table[4]==table[7],
                table[2]==table[5]==table[8],
                table[0]==table[4]==table[8],
                table[2]==table[4]==table[6]
            ]
            for condizione in condizioni_fine:
                if condizione:
                    vinta = True
                    break
            mossa += 1

