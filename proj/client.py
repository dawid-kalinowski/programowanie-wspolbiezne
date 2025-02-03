#!/usr/bin/env python3
import socket
import json
import threading
import tkinter as tk
from tkinter import messagebox

my_color = None
current_turn = None
board_state = None
sock = None

# funkcja rysująca planszę
def draw_board(canvas, board):
    canvas.delete("all")
    cell_size = 50
    for i in range(8):
        for j in range(8):
            x0 = j * cell_size
            y0 = i * cell_size
            x1 = x0 + cell_size
            y1 = y0 + cell_size
            canvas.create_rectangle(x0, y0, x1, y1, fill="#dea6ff", outline="black")
            if board[i][j] == 'B':
                canvas.create_oval(x0+5, y0+5, x1-5, y1-5, fill="black")
            elif board[i][j] == 'W':
                canvas.create_oval(x0+5, y0+5, x1-5, y1-5, fill="white")
    # wyświetlenie informacji o turze
    if current_turn:
        canvas.create_text(200, 10, text=f"Tura: {'Czarny' if current_turn == 'B' else 'Biały'}", fill="yellow", font=("Arial", 16, "bold"))

# funkcja odbierająca dane z serwera
def receive_data(canvas):
    global my_color, current_turn, board_state, sock
    while True:
        try:
            data = sock.recv(2048).decode()
            if not data:
                break
            message = json.loads(data)
            action = message.get("action")
            if action == "start":
                # ustawienie koloru gracza na podstawie wiadomości startowej
                my_color = message.get("color")
                board_state = message.get("board")
                current_turn = message.get("current_turn")
                canvas.after(0, draw_board, canvas, board_state)
            elif action == "update":
                board_state = message.get("board")
                current_turn = message.get("current_turn")
                canvas.after(0, draw_board, canvas, board_state)
            elif action == "error":
                error_msg = message.get("message")
                messagebox.showerror("Błąd", error_msg)
            elif action == "game_over":
                board_state = message.get("board")
                draw_board(canvas, board_state)
                result = message.get("result")
                score = message.get("score")
                msg = f"Koniec gry!\n{result}\nWynik:\Czarny: {score.get('B')}  Biały: {score.get('W')}"
                messagebox.showinfo("Koniec gry", msg)
                sock.close()
                break
        except Exception as e:
            print("Błąd odbioru danych:", e)
            break

# obsługa kliknięcia w planszę
def on_canvas_click(event, canvas):
    global sock, my_color, current_turn
    cell_size = 50
    row = event.y // cell_size
    col = event.x // cell_size
    # jeśli to nie tura gracza, ignorujemy kliknięcie
    if my_color != current_turn:
        messagebox.showwarning("Uwaga", "Nie Twoja tura!")
        return
    move = {"action": "move", "row": row, "col": col}
    try:
        sock.sendall(json.dumps(move).encode())
    except Exception as e:
        print("Błąd wysyłania ruchu:", e)

# funkcja łącząca się z serwerem i uruchamiająca interfejs graficzny
def start_client():
    global sock, my_color, current_turn, board_state
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('localhost', 5000))
    except Exception as e:
        print("Błąd połączenia z serwerem:", e)
        return

    # utworzenie interfejsu graficznego
    root = tk.Tk()
    root.title("Reversi")
    canvas = tk.Canvas(root, width=400, height=400)
    canvas.pack()

    # junkcja odbierania danych z serwera w osobnym wątku
    threading.Thread(target=receive_data, args=(canvas,), daemon=True).start()

    # obsługa kliknięć myszy
    canvas.bind("<Button-1>", lambda event: on_canvas_click(event, canvas))

    # główna pętla interfejsu
    root.mainloop()

if __name__ == "__main__":
    start_client()
