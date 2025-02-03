import sysv_ipc
import time
import os

NULL_CHAR = '\0'
KLUCZ_PW1 = 100 
KLUCZ_PW2 = 101
KLUCZ_SEM1 = 200
KLUCZ_SEM2 = 201

def pisz(mem, s):
    s += NULL_CHAR
    mem.write(s.encode())

def czytaj(mem):
    s = mem.read().decode()
    return s.split(NULL_CHAR)[0]

try:
    sem1 = sysv_ipc.Semaphore(KLUCZ_SEM1, sysv_ipc.IPC_CREX, 0o700, 0)
    sem2 = sysv_ipc.Semaphore(KLUCZ_SEM2, sysv_ipc.IPC_CREX, 0o700, 0)
    pw1 = sysv_ipc.SharedMemory(KLUCZ_PW1, sysv_ipc.IPC_CREX, 0o700, 1024)
    pw2 = sysv_ipc.SharedMemory(KLUCZ_PW2, sysv_ipc.IPC_CREX, 0o700, 1024)
    print("Jestem Graczem 1")
    gracz1 = True
except sysv_ipc.ExistentialError:
    sem1 = sysv_ipc.Semaphore(KLUCZ_SEM1)
    sem2 = sysv_ipc.Semaphore(KLUCZ_SEM2)
    pw1 = sysv_ipc.SharedMemory(KLUCZ_PW1)
    pw2 = sysv_ipc.SharedMemory(KLUCZ_PW2)
    print("Jestem Graczem 2")
    gracz1 = False

wynik_gracz1 = 0
wynik_gracz2 = 0

for tura in range(1, 4):
    print(f"\nTura {tura}")

    if gracz1:
        wybrana_karta = input("Gracz 1: Wybierz pozycję (1, 2, 3): ")
        pisz(pw1, wybrana_karta)
        sem2.release()
        sem1.acquire()

        typowana_karta = czytaj(pw2)
        print(f"Gracz 2 wybrał: {typowana_karta}")

    else:
        sem2.acquire()
        typowana_karta = input("Gracz 2: Zgadnij pozycję (1, 2, 3): ")
        pisz(pw2, typowana_karta)
        sem1.release()

        wybrana_karta = czytaj(pw1)
        print(f"Gracz 1 wybrał: {wybrana_karta}")

    if wybrana_karta == typowana_karta:
        print("Gracz 2 wygrał tę turę!")
        wynik_gracz2 += 1
    else:
        print("Gracz 1 wygrał tę turę!")
        wynik_gracz1 += 1

    print(f"Wynik: Gracz 1 - {wynik_gracz1}, Gracz 2 - {wynik_gracz2}")

if gracz1:
    pw1.remove()
    pw2.remove()
    sem1.remove()
    sem2.remove()
else:
    pw1.detach()
    pw2.detach()

print("\nGra zakończona!")
print(f"Końcowy wynik: Gracz 1 - {wynik_gracz1}, Gracz 2 - {wynik_gracz2}")
if wynik_gracz1 > wynik_gracz2:
    print("Gracz 1 wygrywa!")
elif wynik_gracz2 > wynik_gracz1:
    print("Gracz 2 wygrywa!")
else:
    print("Remis!")
