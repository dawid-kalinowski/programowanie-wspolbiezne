import os
import sys

SERVER_FIFO = "/tmp/server_fifo"

def send_request(id_to_find):
    client_fifo = f"/tmp/client_fifo_{os.getpid()}"
    if not os.path.exists(client_fifo):
        os.mkfifo(client_fifo)

    try:
        request = f"{id_to_find},{client_fifo}"
        
        with open(SERVER_FIFO, "w") as server_fifo:
            server_fifo.write(request)

        with open(client_fifo, "r") as client_fifo_file:
            response = client_fifo_file.read().strip()
            print(f"Odpowiedź od serwera: {response}")

    finally:
        os.unlink(client_fifo)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Użycie: python klient.py <ID>")
        sys.exit(1)

    id_to_find = int(sys.argv[1])
    send_request(id_to_find)
