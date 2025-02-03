import threading

lock = threading.Lock()
suma = 0

# funkcja przyjmuje fragment listy
def sumuj(fragment):
    global suma
    local_sum = sum(fragment) 
    with lock:
        suma += local_sum

# funkcja dzieląca zadanie na wątki
def wielowatkowe_sumowanie(lista, liczba_watkow):
    fragmenty = [lista[i::liczba_watkow] for i in range(liczba_watkow)]  # dzielimy listę na fragmenty
    watki = []

    # tworzymy i uruchamiamy wątki
    for fragment in fragmenty:
        t = threading.Thread(target=sumuj, args=(fragment,))
        watki.append(t)
        t.start()

    # czekamy na zakończenie wszystkich wątków
    for t in watki:
        t.join()


lista = [i for i in range(1, 1000001)]  # lista  od 1 do 1,000,000

liczba_watkow = 4

wielowatkowe_sumowanie(lista, liczba_watkow)

print(f"Wynik: {suma}")
