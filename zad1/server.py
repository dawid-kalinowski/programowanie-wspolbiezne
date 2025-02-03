import time
import os

def calculate(a):
    return 5 * a

def main():
    print("Serwer został uruchomiony pomyślnie")
    while True:
        # jeżeli plik ma dane, to działamy, a jeżeli nie, to nie robimy nic
        if os.path.exists("dane.txt") and os.path.getsize("dane.txt") > 0:

            # sczytujemy dane z pliku
            with open("dane.txt", "r") as file:
                data = int(file.read().strip())

            # obliczamy wynik poprzez funkcję calculate
            result = calculate(data)
            print(f"Dane: {data}, Wynik: {result}")

            # zapisujemy wynik do pliku
            with open("wyniki.txt", "w") as file:
                file.write(str(result))

            # czyścimy plik, żeby serwer nie wykonywał dalej na nim operacji
            open("dane.txt", "w").close()

        # sprawdzamy plik co 0,5 sekundy
        time.sleep(0.5)

if __name__ == "__main__":
    main()