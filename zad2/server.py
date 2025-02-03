import os
import time

SERVER_BUFFER = "server_buffer.txt"
LOCKFILE = "server.lock"

def main():
    print("Serwer uruchomiony")
    while True:
        # jeśli plik blokujący nie istnieje, to czekamy sekundę i sprawdzamy ponownie
        if not os.path.exists(LOCKFILE):
            time.sleep(1)
            continue

        try:
            with open(SERVER_BUFFER, "r") as buffer_file:
                lines = buffer_file.readlines()

            # pierwsza linia to nazwa pliku do odpowiedzi, którą przesłał klient
            client_response_file = lines[0].strip()
            # a pozostałe linie to wiadomość od klienta
            client_message = lines[1:]

            print(f"Otrzymano wiadomość:\n{''.join(client_message)}")

            # odpowiedź serwera
            server_response = []
            print("Wpisz odpowiedź serwera. Może być w wielu liniach, zakończ, wpisując \"exit\"")
            
            while True:
                line = input()
                if line == "exit":
                    break
                server_response.append(line + "\n")

            # zapisujemy odpowiedź do pliku o nazwie podanej przez klienta
            with open(client_response_file, "w") as client_file:
                client_file.writelines(server_response)
                client_file.write("\x1b\n")

            print(f"Odpowiedź została zapisana w pliku: {client_response_file}")

        except Exception as e:
            print(f"Błąd serwera: {e}")

        finally:
            # po zakończeniu operacji usuwamy plik blokujący oraz bufer
            if os.path.exists(LOCKFILE):
                os.remove(LOCKFILE)
            if os.path.exists(SERVER_BUFFER):
                os.remove(SERVER_BUFFER)

if __name__ == "__main__":
    main()
