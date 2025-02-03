import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
BUFFER_SIZE = 1024
CHOICES = {"k": "kamień", "p": "papier", "n": "nożyce"}

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Witaj w kamień, papier, nożyce!")
    print("W każdej chwili możesz zakończyć grę, wpisując 'koniec'.")

    while True:
        choice = input("Wybierz (k - kamień, p - papier, n - nożyce): ").lower()
        if choice not in CHOICES and choice != "koniec":
            print("Nieprawidłowy wybór")
            continue

        # wysyłamy wybór gracza do serwera
        client_socket.sendto(choice.encode("utf-8"), (SERVER_IP, SERVER_PORT))

        if choice == "koniec":
            print("Zakończono grę.")
            break

        # odbieramy wiadomość serwera
        response, _ = client_socket.recvfrom(BUFFER_SIZE)
        print(response.decode("utf-8"))

    # po zakończeniu gry zamykamy socket
    client_socket.close()

if __name__ == "__main__":
    main()
