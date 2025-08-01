import os
import time


def clear_console():
    # Verifica il sistema operativo e usa il comando corretto
    if os.name == 'nt':  # nt è per Windows
        os.system('cls')
    else:  # macOS o Linux
        os.system('clear')


class Client:

    def __init__(self, name, balance):
        self.name = name
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if (self.balance >= amount):
            self.balance -= amount
        else:
            print("Insufficient balance!")


#----------------------CLIENTI
mark = Client("Mark", 30000)
anne = Client("Anne", 5000)
joe = Client("Joe", 15000)

clients = [mark, anne, joe]

while True:
    clear_console()
    #----------------------GRAPHIC
    print("\n\n--------- FRASCO BANK ---------\n\n")
    for i in range(len(clients)):
        print(f"{clients[i].name}: {clients[i].balance}$")
    print("\n")
    nam = input("Client Name: ").strip().capitalize()
    #----------------------CLIENT
    try:
        client = None
        for cli in clients:
            if nam == cli.name:
                client = cli
        if client is None:
            print("Wrong client name! Try again")
            time.sleep(2)
    #----------------------ACTION
        else:
            action = input("Action(Deposit/Withdraw): ").strip().capitalize()
            if (action == "Deposit" or action == "Withdraw"):
                #----------------------AMOUNT
                amn = input("Amount: ")
                try:
                    amn = float(amn)
                except:
                    print("Wrong value! Only positive numbers!")
                    time.sleep(2)
                if amn > 0:
                    if (action == "Deposit"):
                        client.deposit(amn)
                    elif (action == "Withdraw"):
                        if amn <= float(client.balance):
                            client.withdraw(amn)
                        else:
                            print("Insufficent balance!")
                            time.sleep(2)
                else:
                    print("Wrong value! Only positives!")
                    time.sleep(2)
            else:
                print("Wrong action! Choose Deposit/Withdraw")
                time.sleep(2)
    except:
        print("Unexpected error!")
