import os
import time
import sys

SERVER_BUFFER = "server_buffer.txt"
LOCKFILE = "server.lock"

def main():
    client_response_file = input("Podaj nazwę pliku do zapisania odpowiedzi serwera: ").strip()


    print("Wpisz wiadomość do serwera. Może być w wielu liniach, zakończ, wpisując \"exit\"")
    client_message = []
    while True:
        line = input()
        if line == "exit":
            break
        client_message.append(line + "\n")

    # sprawdzanie, czy serwer jest wolny (czy plik blokujący istnieje)
    while os.path.exists(LOCKFILE):
        print("Serwer zajęty, proszę czekać...")
        time.sleep(3)

    try:
        # tworzymy plik blokujący
        with open(LOCKFILE, "w") as lock:
            lock.write("lock")

        # zapisujemy wiadomość do pliku buforu serwera
        with open(SERVER_BUFFER, "w") as buffer_file:
            buffer_file.write(client_response_file + "\n")
            buffer_file.writelines(client_message)
            buffer_file.write("\x1b\n")

        print("Wiadomość wysłana do serwera. Oczekiwanie na odpowiedź...")

        # jeśli serwer nie stworzył pliku z odpowiedzia, to czekamy sekundę i sprawdzamy ponownie
        while not os.path.exists(client_response_file):
            time.sleep(1)

        # otwieramy plik z odpowiedzią i wyświetlamy wiadomość
        with open(client_response_file, "r") as response_file:
            response = response_file.read()
        print("Odpowiedź od serwera:")
        print(response)

    except Exception as e:
        print(f"Błąd klienta: {e}")

    finally:
        # po zakończeniu całej operacji, usuwamy plik blokujący
        if os.path.exists(LOCKFILE):
            os.remove(LOCKFILE)

if __name__ == "__main__":
    main()
