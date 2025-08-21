import random

#---------------------
#-------TARGETS-------

_PIL = 2000000000000  # PIL iniziale
_tasso = 0.02         # Tasso d'interesse iniziale
_spesa_pub = 1000000000000 # Spesa pubblica iniziale
_tasse = 0.3          # Tasse iniziali

_cambio = 1.10        # Cambio EUR/USD
_infl = 0.02          # Inflazione iniziale
_disocc = 0.05        # Disoccupazione iniziale
_NRU = 0.05           # Natural Rate of Unemployment
_bilancio = 0         # Bilancio statale iniziale

#---------------------
#-------ACTUAL--------

PIL = _PIL
tasso = _tasso
spesa_pub = _spesa_pub
tasse = _tasse

cambio = _cambio
infl = _infl
disocc = _disocc
NRU = _NRU
bilancio = _bilancio
anno = -1

#-------LOOP-------
while True:
    try:
        print(f"\n\nSituazione anno {anno+1}:\n- PIL: {int(PIL)}€\n- Cambio: {round(cambio,4)} EUR/USD\n- Inflazione: {round(infl * 100,4)}%\n- Disoccupazione: {round(disocc * 100,4)}%\n- NRU (Disoccupazione Naturale): {round(NRU * 100,4)}%\n- Bilancio statale: {int(bilancio)}€\n\n")
        anno += 1
        # Input da parte dell'utente
        tasso = float(input("Tasso BCE nuovo (senza %, con punto, es 1.75): ")) / 100
        spesa_pub = float(input("Spesa pubblica (in €): "))
        tasse = float(input("Tasse percentuale nuove (senza %, con punto, es 44.25): ")) / 100
        #--------INFL--------
        infl = round(infl + infl * random.uniform(((_tasso / tasso) - 1) * 0.2, ((_tasso / tasso) - 1) * 0.24), 4)
        
        #----PIL & REAL PIL-----
        PIL = int(PIL + PIL * random.uniform(((infl / _infl) - 1) * 0.3, ((infl / _infl) - 1) * 0.25))
        real_PIL = PIL / (1 + infl)
        
        #-------DISOCC-------
        disocc = round(disocc + disocc * random.uniform(((_PIL / real_PIL) - 1) * 0.9, ((_PIL / real_PIL) - 1) * 0.85), 4)
        
        #-------CAMBIO--------
        cambio = round(cambio + cambio * (((_infl / infl
        ) - 1) * 0.1), 4)
        
        #------BILANCIO-------
        bilancio += spesa_pub - (tasse * PIL)  # Aggiorna il bilancio in base alla spesa e alle tasse
    except:
        print("ERRORE: non inviare dati nulli, invalidi o malformattati")