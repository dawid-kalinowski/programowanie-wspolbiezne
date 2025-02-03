#!/usr/bin/env python3
import socket
import threading
import json


class ReversiBoard:
    def __init__(self):
        # plansza 8x8 – puste pola oznaczamy spacją ' '
        self.board = [[' ' for _ in range(8)] for _ in range(8)]
        # ustawienie początkowe pionków jak w skrypcie, białe d4 i e5 (3,3 i 4,4), czarne e4 i d5 (3,4  i 4,3)
        self.board[3][3] = 'W'
        self.board[3][4] = 'B'
        self.board[4][3] = 'B'
        self.board[4][4] = 'W'

    def in_bounds(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def opponent(self, player):
        return 'W' if player == 'B' else 'B'

    # sprawdzenie, czy ruch jest poprawny
    def is_valid_move(self, row, col, player):
        if not self.in_bounds(row, col) or self.board[row][col] != ' ':
            return False
        opp = self.opponent(player)
        directions = [(-1,-1), (-1,0), (-1,1),
                      (0,-1),         (0,1),
                      (1,-1),  (1,0), (1,1)]
        for dx, dy in directions:
            r, c = row + dx, col + dy
            found_opponent = False
            # pierwszy sąsiad musi należeć do przeciwnika
            if self.in_bounds(r, c) and self.board[r][c] == opp:
                found_opponent = True
                r += dx
                c += dy
                # szukamy kontynuacji linii z przeciwnikami
                while self.in_bounds(r, c) and self.board[r][c] == opp:
                    r += dx
                    c += dy
                # jeśli skończyliśmy na naszym pionku, ruch jest poprawny
                if found_opponent and self.in_bounds(r, c) and self.board[r][c] == player:
                    return True
        return False

    # zastosowanie ruchu, czyli umieszczenie pionka oraz przejęcie pól przeciwnika
    def apply_move(self, row, col, player):
        self.board[row][col] = player
        opp = self.opponent(player)
        directions = [(-1,-1), (-1,0), (-1,1),
                      (0,-1),         (0,1),
                      (1,-1),  (1,0), (1,1)]
        for dx, dy in directions:
            r, c = row + dx, col + dy
            pieces_to_flip = []
            # szukamy sekwencji pionków przeciwnika w danym kierunku
            while self.in_bounds(r, c) and self.board[r][c] == opp:
                pieces_to_flip.append((r, c))
                r += dx
                c += dy
            # jeśli ciąg zakończył się pionkiem gracza, zamieniamy pionki przeciwnika w linii
            if pieces_to_flip and self.in_bounds(r, c) and self.board[r][c] == player:
                for rr, cc in pieces_to_flip:
                    self.board[rr][cc] = player

    #  zwraca tablicę dostępnych ruchów
    def get_valid_moves(self, player):
        moves = []
        for row in range(8):
            for col in range(8):
                if self.is_valid_move(row, col, player):
                    moves.append((row, col))
        return moves
    # sprawdza czy plansza nie jest już wypełniona
    def is_full(self):
        for row in self.board:
            for cell in row:
                if cell == ' ':
                    return False
        return True
    # zlicza ilość pionków poszczególnego gracza na planszy
    def count_pieces(self):
        black = sum(row.count('B') for row in self.board)
        white = sum(row.count('W') for row in self.board)
        return black, white

    # gra kończy się, jeśli plansza jest pełna lub obaj gracze nie mają dostępnych ruchów
    def is_game_over(self):
        if self.is_full():
            return True
        if not self.get_valid_moves('B') and not self.get_valid_moves('W'):
            return True
        return False

board = ReversiBoard()
clients = {}  # słownik: klucz = kolor (B lub W), wartość = socket
lock = threading.Lock()
current_turn = 'B'  # grę rozpoczyna czarny gracz

# wysyła wiadomość do wszystkich klientów
def broadcast(message):
    for conn in clients.values():
        try:
            conn.sendall(json.dumps(message).encode())
        except Exception as e:
            print("Błąd wysyłania do klienta:", e)

#  wysyła aktualny stan gry (planszę i informacje o turze)
def send_update():
    global board, current_turn
    msg = {
        "action": "update",
        "board": board.board,
        "current_turn": current_turn
    }
    broadcast(msg)

# funkcja obsługująca komunikację z pojedynczym klientem
def client_thread(conn, player_color):
    global board, current_turn
    # Połączenie – wysłanie wiadomości startowej z przydzielonym kolorem i stanem planszy
    try:
        start_msg = {
            "action": "start",
            "color": player_color,
            "board": board.board,
            "current_turn": current_turn
        }
        conn.sendall(json.dumps(start_msg).encode())
    except Exception as e:
        print("Błąd wysyłania startowej wiadomości:", e)
        return

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            message = json.loads(data)
            if message.get("action") == "move":
                row = message.get("row")
                col = message.get("col")
                with lock:
                    # sprawdzamy, czy właściwy gracz wykonuje ruch
                    if player_color != current_turn:
                        err = {"action": "error", "message": "Nie Twoja tura!"}
                        conn.sendall(json.dumps(err).encode())
                        continue
                    # sprawdzamy, czy ruch jest prwidłowy
                    if not board.is_valid_move(row, col, player_color):
                        err = {"action": "error", "message": "Niepoprawny ruch"}
                        conn.sendall(json.dumps(err).encode())
                        continue
                    # wykonanie ruchu
                    board.apply_move(row, col, player_color)
                    # sprawdzamy, czy przeciwnik ma dostępne ruchy
                    opp = board.opponent(player_color)
                    if board.get_valid_moves(opp):
                        current_turn = opp
                    elif board.get_valid_moves(player_color):
                        # przeciwnik nie ma ruchu, więc obecny gracz ma turę
                        current_turn = player_color
                    else:
                        # gdy żaden z graczy nie ma ruchu, gra kończy się
                        current_turn = None

                    # wysyłamy zaktualizowany stan planszy do obu graczy
                    send_update()

                    # przy każdym ruchu sprawdzamy, czy gra się zakończyła
                    if board.is_game_over():
                        black, white = board.count_pieces()
                        if black > white:
                            result = "Czarny wygrał!"
                        elif white > black:
                            result = "Biały wygrał!"
                        else:
                            result = "Remis!"
                        end_msg = {"action": "game_over", "result": result, "board": board.board, "score": {"B": black, "W": white}}
                        broadcast(end_msg)
                        break
        except Exception as e:
            print("Błąd w komunikacji z klientem:", e)
            break
    conn.close()
    print(f"Klient {player_color} rozłączył się.")

# funkcja startująca serwer – oczekuje na dwóch graczy
import random

def start_server():
    global clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 5000))
    server_socket.listen(2)
    print("Serwer oczekuje na graczy na porcie 5000...")

    # lista dostępnych kolorów
    available_colors = ['B', 'W']
    
    # akceptujemy pierwszego gracza
    conn1, addr1 = server_socket.accept()
    # losowo wybieramy kolor dla pierwszego gracza
    color1 = random.choice(available_colors)
    # usuwamy wybrany kolor z listy, by drugi gracz dostał pozostały kolor
    available_colors.remove(color1)
    print(f"Gracz {color1} połączył się z {addr1}")
    clients[color1] = conn1
    threading.Thread(target=client_thread, args=(conn1, color1), daemon=True).start()

    # akceptujemy drugiego gracza i przydzielamy mu pozostały kolor
    conn2, addr2 = server_socket.accept()
    color2 = available_colors[0]  # jedyny pozostały kolor
    print(f"Gracz {color2} połączył się z {addr2}")
    clients[color2] = conn2
    threading.Thread(target=client_thread, args=(conn2, color2), daemon=True).start()

    # serwer działa, aż gra się zakończy
    while True:
        with lock:
            if board.is_game_over():
                break


if __name__ == "__main__":
    start_server()

