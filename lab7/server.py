import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
BUFFER_SIZE = 1024
CHOICES = {"k": "kamień", "p": "papier", "n": "nożyce"}

def determine_winner(choice1, choice2): # funkcja przyjmuje wybor gracza1 i wybor gracza2
    if choice1 == choice2:
        return 0  # remis
    if (choice1 == "k" and choice2 == "n") or (choice1 == "p" and choice2 == "k") or (choice1 == "n" and choice2 == "p"):
        return 1  # gracz1 wygrywa
    return 2  # gracz2 wygrywa

def main():
    # tworzymy socket serwera
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    print(f"Serwer działa na {SERVER_IP}:{SERVER_PORT}")

    players = {}  # {adres: wybór}
    scores = {}   # {adres: punkty}

    while True:
        data, address = server_socket.recvfrom(BUFFER_SIZE)
        message = data.decode("utf-8")

        # któryś z graczy kończy grę
        if message == "koniec":
            print(f"Gracz {address} zakończył grę.")
            other_player = next((p for p in players if p != address), None)
            if other_player:
                server_socket.sendto("koniec".encode("utf-8"), other_player)
            players.clear()
            scores.clear()
            print("Koniec gry, oczekiwanie na nowych graczy")
            continue

        # nowy gracz dołącza do gry
        if address not in scores:
            scores[address] = 0
            print(f"Nowy gracz: {address}")

        players[address] = message
        print(f"Odebrano od {address}: {CHOICES.get(message, 'Nieznany wybór')}")

        # gdy dwóch graczy dokonało wyboru
        if len(players) == 2:
            player_addresses = list(players.keys())
            player_choices = list(players.values())

            winner = determine_winner(player_choices[0], player_choices[1])

            if winner == 0:
                result = "Remis"
            elif winner == 1:
                result = f"Wygrywa gracz {player_addresses[0]}"
                scores[player_addresses[0]] += 1
            else:
                result = f"Wygrywa gracz {player_addresses[1]}"
                scores[player_addresses[1]] += 1

            # informowanie graczy o wynikach
            for i, addr in enumerate(player_addresses):
                opponent_choice = player_choices[1 - i]
                response = f"Przeciwnik wybrał {CHOICES[opponent_choice]}. {result} Punkty: {scores}"
                server_socket.sendto(response.encode("utf-8"), addr)

            # po zakończeniu rundy resetujemy wybory
            players.clear()

if __name__ == "__main__":
    main()
