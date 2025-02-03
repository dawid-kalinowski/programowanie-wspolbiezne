import os
import sys
import re

# regex do wyszukiwania: \input{nazwapliku.rozszerzenie}
INPUT_PATTERN = r"\\input\{(.+?)\}"

def count_word_occurrences(filename, target_word):
    word_count = 0
    processes = []  # tablica z PID procesów potomnych

    def read_file(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return f.readlines()
        except FileNotFoundError:
            print(f"Błąd: Plik {file} nie istnieje.")
            return []

    # wczytanie zawartości pliku
    lines = read_file(filename)

    for line in lines:
        # sprawdzamy, czy dana linia zawiera \input{plik}
        match = re.search(INPUT_PATTERN, line)
        if match:
            # jeśli znajdzie, to tworzymy proces potomny
            included_file = match.group(1)
            pid = os.fork()  # tworzymy proces potomny
            if pid == 0:
                # pid procesu potomnego
 
                result = count_word_occurrences(included_file, target_word)
                print("dizecko" + str(pid) + ": " + str(result))
                os._exit(result)  # zwracamy wynik jako kod wyjścia procesu
            else:
                # pid procesu rodzica
                print("rodzic" + str(pid))
                processes.append(pid)
        
        # zliczamy wystąpienia słowa w danej linii tekstu
        word_count += len(re.findall(rf"\b{re.escape(target_word)}\b", line, re.IGNORECASE))

   # czekamy na zakończenie procesów i sumujemy licznik wystąpień słowa
    for pid in processes:
        _, status = os.waitpid(pid, 0)
        word_count += os.WEXITSTATUS(status)
        print("word count po dodaniu procesu " + str(pid) + " :" + str(word_count))

    return word_count

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Użycie programu: python main.py <plik_początkowy> <słowo>")
        sys.exit(1)

    start_file = sys.argv[1]
    search_word = sys.argv[2]

    total_count = count_word_occurrences(start_file, search_word)
    print(f"Słowo '{search_word}' występuje {total_count} razy w tekście.")
