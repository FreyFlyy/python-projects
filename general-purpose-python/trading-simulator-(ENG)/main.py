###TRADING SIMULATOR
#IMPORTS
import random
import time
import os

#CLEAR FUNCTION
def clear():
    if os.name == 'nt':     # Windows
        os.system('cls')
    else:                   # Linux, macOS
        os.system('clear')

#INITIALIZATION
price_start = 100
price = 100
balance = int(input("Starting balance: (integer number): "))
owned = 0

###CYCLE
while True:
  ###SHOW MARKET FOR 5 SEC
  for i in range(0,50):
    clear()
    price = round(price*(random.randint(99,101))/100,2)
    print(f"--------- Price: {price} --------- \n\n")
    print("|"*int((price-60)))
    print(" "*(price_start-61) + "^")
    print(" "*(price_start-62) + "100")
    time.sleep(0.1)
  ###PROBABILITIES
  if price < price_start:
    #RISING
    print(f"\nProbability of price raising: {round((0.5+(abs(price-price_start)/max(price,price_start)))*100,2)}%")
    print(f"Balance: {round(balance,2)}$")
  elif price > price_start:
    #FALLING
    print(f"\nProbability of price falling: {round((0.5+(abs(price-price_start)/max(price,price_start)))*100,2)}%")
    print(f"Balance: {round(balance,2)}$")
  elif price == price_start:
    #NONE
    print(f"\nProbability of price rising/falling: 50%")
    print(f"Balance: {round(balance,2)}$")
  ###BUY SELL NONE
  choose = input("\n---\n\nBuy (B) / Sell ALL (S) / None (N):")
  
  #BUY
  if choose.strip().upper() == "B":
    amnt = int(input("Amount to buy (integer): "))
    if balance >= amnt*round(price,2):
      balance -= amnt*round(price,2)
      owned += amnt
      print(f"\nBought {amnt} units at {round(price,2)}$")
      print(f"Balance: {round(balance,2)}")
      time.sleep(3)
    else:
      print("\nCannot buy now, insufficient balance")
      time.sleep(2)
  #SELL
  elif choose.strip().upper() == "S":
    balance += (owned*round(price,2))
    print(f"\nSold all {owned} units")
    print(f"Balance: {round(balance,2)}")
    owned = 0
    time.sleep(3)
  
  
  
  
  
