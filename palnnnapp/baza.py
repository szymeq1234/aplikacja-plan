import sqlite3

# Połączenie z bazą danych (tworzy plik jeśli nie istnieje)
poloczenie = sqlite3.connect("cos.sqlite")
cursor = poloczenie.cursor()

# Włączenie obsługi kluczy obcych
cursor.execute("PRAGMA foreign_keys = ON;")

# Otwieramy plik ze schematem bazy i wykonujemy go
with open("dane_schemat.sql", "r", encoding="utf-8") as file:
    cursor.executescript(file.read())

# Zatwierdzamy zmiany i zamykamy połączenie
poloczenie.commit()
poloczenie.close()

print("Baza danych została zainicjalizowana!")

conn = sqlite3.connect("cos.sqlite")
cursor = conn.cursor()
cursor.execute("INSERT INTO Nauczyciele (nazwisko) VALUES (?)", ("maciag",))
cursor.execute("INSERT INTO Nauczyciele (nazwisko) VALUES (?)", ("kowalczyk",))
cursor.execute("INSERT INTO Nauczyciele (nazwisko) VALUES (?)", ("augustyniak",))

conn.commit()
conn.close()