import matplotlib.pyplot as plt
import math
import time

print("\nUn programma che simula lo spazio con N corpi che si attraggono a vicenda\n\nFa una simulazione del sistema solare semplificata, solo fino a marte, per motivi di tempo e calcolo\n\n------\n\nAspettare...\n")

###CLASSE CORPO
class Corpo:
    def __init__(self, w, x, y, vx, vy):
        self.w = w  # massa
        self.x = x  # posizione x
        self.y = y  # posizione y
        self.vx = vx  # velocità lungo x
        self.vy = vy  # velocità lungo y

###CORPI
corpi = [
    # Sole
    Corpo(1.989 * 10**30, 0, 0, 0.0, 0.0),
    # Mercurio
    Corpo(3.285 * 10**23, 5.8 * 10**10, 0, 0.0, 47892),
    # Venere
    Corpo(4.867 * 10**24, 1.082 * 10**11, 0, 0.0, 35020),
    # Terra
    Corpo(5.972 * 10**24, 1.47 * 10**11, 0, 0.0, 29783), 
    # Marte
    Corpo(6.417 * 10**23, 2.28 * 10**11, 0, 0.0, 24077)
]



#LISTE TRAIETTORIE
tracce_x = [[] for _ in corpi]
tracce_y = [[] for _ in corpi]

#VALORI
dt = 1000  #PASSO TEMPORALE
T = 0      #TEMPO INIZIALE
G = 6.67 * 10**-11  #COSTANTE GRAVITAZIONALE

###FUNZIONE  
def step(corpi):
    n = len(corpi)
    for i in range(n):
        for j in range(i + 1, n):
            co1, co2 = corpi[i], corpi[j]
            
            #DISTANZA
            dx = co2.x - co1.x
            dy = co2.y - co1.y
            r2 = dx**2 + dy**2
            r = max(math.sqrt(r2), 1e-3)  #NO DIVISIONI PER 0
            
            #FORZA GRAVITAZIONALE
            f = G * co1.w * co2.w / r2
            
            #COMPONENTI X E Y
            fx = f * (dx / r)
            fy = f * (dy / r)
            
            #ACCELERAZIONE
            a1x = fx / co1.w
            a1y = fy / co1.w
            a2x = -fx / co2.w
            a2y = -fy / co2.w
            
            #VELOCITA
            co1.vx += a1x * dt
            co1.vy += a1y * dt
            co2.vx += a2x * dt
            co2.vy += a2y * dt
    
    #POSIZIONE
    for corpo in corpi:
        corpo.x += corpo.vx * dt
        corpo.y += corpo.vy * dt

#ANNO IN SECONDI
anno = 365.25 * 24 * 3600

start_time = time.time()

###CICLO PRINCIPALE
while T <= 12*anno:
    step(corpi)
    for i, corpo in enumerate(corpi):
        tracce_x[i].append(corpo.x)
        tracce_y[i].append(corpo.y)
    T += dt

#CALCOLO TEMPO IMPIEGATO
end_time = time.time()
execution_time = end_time - start_time
print(f"Tempo di esecuzione: {round(execution_time, 2)} secondi\n\nSe competenti, è anche modificabile a proprio piacimento")

###PLOT TRAIETTORIE
for i, (x, y) in enumerate(zip(tracce_x, tracce_y)):
    plt.plot(x, y)
    plt.scatter(x[0], y[0])
plt.xlabel("Posizione X (m)")
plt.ylabel("Posizione Y (m)")
plt.title("Simulazione di N corpi sotto gravità")
ax = plt.gca()
ax.set_aspect('equal', adjustable='box')
plt.grid()
plt.show()
