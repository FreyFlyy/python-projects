import random
password = "1234"
menu = {
    
    "Bevande":[["Acqua",2],["Coca-cola",3]],
    "Antipasti":[["Calzone alla griglia",5],["Patatine fritte",5]],
    "Primi":[["Pasta al ragù",7],["Lasagne alla bolognese",8]],
    "Secondi":[["Bistecca di manzo",14]],
    "Pizze":[["Margherita",6],["Diavola",8]],
    "Dolci":[["Cheesecake ai lamponi",5],["Sorbetto al limone",4]],
}

tipi = list(menu.keys())
while True:
    scontr = []
    scontrino = ""
    conto = 0
    ancora = True
    found = False
    ce = False
    print("\n\n-------------------  PIZZERIA PIZZA  -------------------\nCosa di desidera fare?\n\n[1] Guarda menù\n[2] Prenota un tavolo\n[3] Ordina d'asporto\n[0] Modifica menù (Solo Autorizzati)")
    scelta = input(">")
    if scelta.strip() == "1":
        print("\n------------  MENU  ------------")
        for tipo in tipi:
            print(f"\n--- {tipo.upper()} ---")
            for cibo in menu[tipo]:
                print(f"{cibo[0]}: {cibo[1]}€")
        print("\n--------------------------------\n\n")
        input("Premi invio per tornare indietro")
    elif scelta.strip() == "2":
        print("\n--------------------------------\n")
        print("Cell: 914 611 5025\nwww.pizzeriapizza.com")
        print("\n--------------------------------\n\n")
        input("Premi invio per tornare indietro")
    elif scelta.strip() == "3":
        while ancora:
            ordine = input("Cosa vuole ordinare? ").strip().capitalize()
            for tipo in tipi:
                for cibo in menu[tipo]:
                    if cibo[0] == ordine:
                        ce = True
                        qta = float(input("Quanti? "))
                        if (qta > 0) and (int(qta) == float(qta)):
                            for volte in range(0,int(qta)):
                                scontr.append(cibo)
                            conto = conto + (cibo[1]) * int(qta)
                        else:
                            input("Selezionare una quantità valida, premere invio per tornare")
            if not ce:
                input("Mi spiace, non lo vendiamo, premi Invio per tornare")
            altro = input("Altro(S/N)? ").strip().upper()
            if altro == "S":
                ancora = True
            else:
                ancora = False
        print(f"\nPerfetto, il conto è di {conto}€\nEcco lo scontrino\n\n")
        scontrino += "------------\n"
        for item in scontr:
            scontrino += f"\n{item[0]}: {item[1]}€"
        scontrino += f"\n\nTOTALE: {conto}€\n\n------------"
        ordnum = ""
        for i in range(0,8):
            ordnum += str(random.randint(0,9))
        print(scontrino+f"\n\nOrdine N° {ordnum}\nP.IVA: 19414201428\nPagamento a: 5198 9837 4487 1941\n\n")
        input("Premi invio per tornare")
    elif scelta.strip() == "0":
        pwd = input("Ciao,\npassword: ")
        if pwd.strip() == password:
            categoria = input("Che categoria modificare?: ").strip().capitalize()
            if categoria in tipi:
                pietanza = input("Che cibo?: ").strip().capitalize()
                for i, item in enumerate(menu[categoria]):
                    if pietanza == item[0]:
                        found = True
                        nuova_pietanza = input("Con cosa sostituire?: ").strip().capitalize()
                        costo = input("Che costo?: ").strip()
                        item[0] = nuova_pietanza
                        item[1] = int(costo)
                        input("Cambiamento effettuato! Premi invio per tornare")
                if not found:
                   input("Mi spiace, pietanza non riconosciuta, premi invio per ricominciare")
            else:
                input("Mi spiace, categoria non riconosciuta, premi invio per ricominciare")
        else:
            input("Password errata, premi invio per ricominciare")
    else:
        input("Comando sconosciuto, premi invio per ricominciare")
