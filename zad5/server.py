# source myenv/bin/activate

import sysv_ipc
import time

klucz_wejsciowy = 11
klucz_wyjsciowy = 12

kolejka_wejsciowa = sysv_ipc.MessageQueue(klucz_wejsciowy, sysv_ipc.IPC_CREAT)
kolejka_wyjsciowa = sysv_ipc.MessageQueue(klucz_wyjsciowy, sysv_ipc.IPC_CREAT)

slownik = {
    'hello': 'cześć',
    'world': 'świat',
    'apple': 'jabłko',
    'computer': 'komputer'
}

while True:
    message, pid = kolejka_wejsciowa.receive(True)

    word = message.decode()
    print(f"Serwer odebrał zapytanie o słowo '{word}'")

    time.sleep(2)

    if word in slownik:
        response = slownik[word]
    else:
        response = "Nie znam takiego słowa"

    kolejka_wyjsciowa.send(response.encode(), pid)
