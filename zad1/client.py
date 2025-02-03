import time
import os


def main():
    user_input = int(input("Podaj liczbę całkowitą: "))

    with open("dane.txt", "w") as file:
        file.write(str(user_input))

    print("Oczekiwanie na wynik...")

    while True:
        if os.path.exists("wyniki.txt") and os.path.getsize("wyniki.txt") > 0: # sprawdzamy, czy wynik już istnieje
            with open("wyniki.txt", "r") as file:
                result = file.read().strip()
            print(f"Wynik: {result}")

            open("wyniki.txt", "w").close()  # czyścimy plik
            break

        time.sleep(0.5) # powtarzamy czynność co 0,5 sekundy

if __name__ == "__main__":
    main()