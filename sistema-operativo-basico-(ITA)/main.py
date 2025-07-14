import time
import os

def name_ok_string(string):
    ok = True
    for char in chars_not_name_ok:
        if char in string:
            ok = False
            break
    return ok
def address_to_dir(adr):
    if "/" in adr:
        adrs = adr.split("/")
        return adrs[-1]
    else:
        return adr
def clear():
    if os.name == 'nt':     # Windows
        os.system('cls')
    else:                   # Linux, macOS
        os.system('clear')
    print("----- FRASCO OS -----")
def filetype(fil):
    return fil.split(".")[-1]

dir = {"home": []}
address_ext = "home"
address = address_to_dir(address_ext).lower()
address_content = dir[address]

chars_not_name_ok = ["/", "?"]
files_txt = []
comandi_base = ["restart", "show", "create", "remove", "rename", "goto", "open", "write"]
    
print("----- FRASCO OS -----\nAttenzione: un file senza estensioni sarà considerato una cartella in FRASCO")

while True:
    ### COMANDO E DECIFRAZIONE
    comando_ = input(f"\n  {address_ext}>> ")
    comando_ = comando_.split(" ")
    comando = []
    for com in comando_:
        if com != "":
            comando.append(com.strip())
            
    if comando[0] == "":
        continue
    elif comando[0] == "?help":
        print("\n---\nAiuto:\n\nrestart: ripulisce il terminale\nshow: mostra i file della directory attuale\ncreate [nome]: crea un file con nome ed estensione personalizzata\nremove [nome]: elimina un file dato il nome (con estensione)\nrename [vecchio] [nuovo]: rinomina un file dato il nome originale e nuovo\ngoto [cartella o --]: vai ad una sottocartella o torna indietro (--)\nopen [nome]: Apre un file .txt\nwrite [nome]: Sovrascrive il testo di un file .txt (sucessivamente si inserirà il testo)")
    elif comando[0] == "restart":
        clear()
    elif comando[0] == "show":
        if len(comando) == 1: #lungo 1
            if address_content == []:
                print("/")
            else:
                for file in address_content:
                    print(file)
    elif comando[0] == "create":
        if (len(comando) == 2) and (name_ok_string(comando[1])) and (comando[1] not in address_content): #lungo 2 e nome_ok e non esiste
            address_content.append(comando[1])
            if not "." in comando[1]:
                dir.update({comando[1]:[]})
            if filetype(comando[1]) == "txt":
                files_txt.append([comando[1], None])
            print(f'"{comando[1]}" creato in {address}')
        else:
            print("ERRORE: comando errato, file già esistente o nome non valido")
    elif comando[0] == "remove":
        if (len(comando) == 2) and (comando[1] in address_content): #lungo 2 e esiste
            address_content.remove(comando[1])
            if filetype(comando[1]) == "txt":
                for file in files_txt:
                    if file[0] == comando[1]:
                        files_txt.remove(file)
                        break
            print(f'"{comando[1]}" rimosso da {address}')
        else:
            print("ERRORE: comando errato o file non esistente")
    elif comando[0] == "rename":
            if (len(comando) == 3) and (comando[1] in address_content) and (name_ok_string(comando[2])): #lungo 3 e esiste e
                indx = address_content.index(comando[1])
                address_content[indx] = comando[2]
                if filetype(comando[1]) == "txt":
                    for file in files_txt:
                        if file[0] == comando[1]:
                            files_txt.remove(file)
                            if filetype(comando[2]) == "txt":
                                files_txt.append([comando[2], None])
                        break
                print(f'"{comando[1]}" rinominato in {comando[2]}')
            else:
                print("ERRORE: comando errato, file non esistente o nome non valido")
    elif comando[0] == "goto":
            if (len(comando) == 2) and ((comando[1] in address_content and not "." in comando[1]) or comando[1] == "--"): #lungo 2 e (esiste o indietro)
                if comando[1] == "--" and address != "home":
                    address_ext = address_ext[:(len(address_ext)-len(address)-1)]
                elif comando[1] == "--" and address == "home":
                    continue
                else:
                    address_ext += f"/{comando[1]}"
            else:
                print("ERRORE: comando errato o indirizzo non valido")
    elif comando[0] == "open":
        if (len(comando) == 2) and (comando[1] in address_content) and (".txt" in comando[1]): #lungo 2 e esiste e file.txt
            for file in files_txt:
                if file[0] == comando[1]:
                    print(file[1])
        else:
            print("ERRORE: comando errato, file non esistente o indirizzo non valido")
    elif comando[0] == "write":
        if (len(comando) == 2) and (comando[1] in address_content) and (".txt" in comando[1]): #lungo 2 e esiste e file.txt
            for file in files_txt:
                if file[0] == comando[1]:
                    testo = input("Testo>>")
                    file[1] = testo
        else:
            print("ERRORE: comando errato, file non esistente o indirizzo non valido")

    else:
        print(f'"{comando[0]}" sconosciuto, riprova o digita ?help per aiuto ')

    address = address_to_dir(address_ext).lower()
    address_content = dir[address]
        
        
        
