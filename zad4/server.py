import os

SERVER_FIFO = "/tmp/server_fifo"

DATABASE = {
    1: "Kowalski",
    2: "Nowak",
    3: "Wiśniewski",
    4: "Wójcik",
    5: "Kowalczyk",
}

def handle_request(request):

    try:
        id_to_find, client_queue = request.split(",")
        id_to_find = int(id_to_find.strip())
        

        response = DATABASE.get(id_to_find, "Nie ma")
        

        with open(client_queue, "w") as client_fifo:
            client_fifo.write(response)
    except Exception as e:
        print(f"Błąd podczas obsługi żądania: {e}")

def main():
    if not os.path.exists(SERVER_FIFO):
        os.mkfifo(SERVER_FIFO)

    print("Serwer gotowy.")

    try:
        while True:
            with open(SERVER_FIFO, "r") as server_fifo:
                request = server_fifo.read().strip()
                handle_request(request)
    except KeyboardInterrupt:
        print("\nZamykanie serwera...")
    finally:
        os.unlink(SERVER_FIFO)

if __name__ == "__main__":
    main()
