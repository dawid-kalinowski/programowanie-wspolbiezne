import sysv_ipc
import time
import os

klucz_wejsciowy = 11
klucz_wyjsciowy = 12

kolejka_wejsciowa = sysv_ipc.MessageQueue(klucz_wejsciowy)
kolejka_wyjsciowa = sysv_ipc.MessageQueue(klucz_wyjsciowy)

pid = os.getpid()

queries = ['hello', 'world', 'apple', 'computer', 'unknown']

for query in queries:
    print(f"Klient wysłał zapytanie '{query}'")
    kolejka_wejsciowa.send(query.encode(), pid)

    response, _ = kolejka_wyjsciowa.receive(True)
    print(f"Klient otrzymał odpowiedź '{response.decode()}'")

