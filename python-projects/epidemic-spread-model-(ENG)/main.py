import matplotlib.pyplot as plt

print("----- SIR epidemic spread model -----\n(susceptible, infected, recovered)\nFor more info visit en.wikipedia.org/wiki/Compartmental_models_in_epidemiology\n\n\n")


# S = S - SIa
# I = I + SIa
# R = R - Rb

a = float(input("Infectious factor (probability percent ex. 7.5): "))/100
b = float(input("Healing factor (probability percent ex. 7.5): "))/100

i_start = float(input("Starting infected (percent ex. 7.5): "))

cycles = int(input("Iterations to simulate(integer): "))

x = [j for j in range(cycles+1)]
s = [100-i_start]
i = [i_start]
r = [0]

for k in range(cycles):
  infected = int(s[k]*i[k]*a)
  recovered = int(i[k]*b)
  
  s.append(max(s[k] - infected,0))
  i.append(min(max(i[k] + infected - recovered,0),100))
  r.append(min(r[k] + recovered,100))

  
plt.plot(x, s, color="blue")
plt.plot(x, i, color="red")
plt.plot(x, r, color="green")

plt.show()




