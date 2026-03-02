PRAGMA foreign_keys = ON; -- Włączenie obsługi kluczy obcych

CREATE TABLE IF NOT EXISTS Nauczyciele (
    Id_Nauczyciela INTEGER PRIMARY KEY NOT NULL,
    Nazwisko TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Klasy (
    Id_Klasy INTEGER PRIMARY KEY NOT NULL,
    Nazwa TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Przedmioty (
    Id_Przedmiotu INTEGER PRIMARY KEY NOT NULL,
    nazwa_p TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Przypisanie (
    Id_przypisania INTEGER PRIMARY KEY NOT NULL,
    Id_lekcji INTEGER NOT NULL,
    Id_Nauczyciela INTEGER NOT NULL,
    Id_Przedmiotu INTEGER,
    FOREIGN KEY (Id_Nauczyciela) REFERENCES Nauczyciele(Id_Nauczyciela),
    FOREIGN KEY (Id_Przedmiotu) REFERENCES Przedmioty(Id_Przedmiotu)
);

CREATE TABLE IF NOT EXISTS Dzielenia (
    Id_podzialu INTEGER PRIMARY KEY NOT NULL,
    Id_dzielenia INTEGER NOT NULL,
    Id_Klasy INTEGER NOT NULL,
    Id_Przedmiotu INTEGER NOT NULL,
    Id_Nauczyciela INTEGER NOT NULL,
    Czy_dzielona BOOLEAN NOT NULL,
    Godzina INTEGER,
    gr1 INTEGER,
    gr2 INTEGER,
    gr3 INTEGER,
    FOREIGN KEY (Id_Klasy) REFERENCES Klasy(Id_Klasy),
    FOREIGN KEY (Id_Nauczyciela) REFERENCES Nauczyciele(Id_Nauczyciela),
    FOREIGN KEY (Id_Przedmiotu) REFERENCES Przedmioty(Id_Przedmiotu)
    );

CREATE TABLE IF NOT EXISTS Klasy_Nauczyciele (
    Id_klasa_nauczyciel INTEGER PRIMARY KEY NOT NULL,
    Id_Nauczyciela INTEGER NOT NULL,
    Czy_loczony_naucz BOOLEAN NOT NULL,
    FOREIGN KEY (Id_Nauczyciela) REFERENCES Nauczyciele(Id_Nauczyciela)
    );

CREATE TABLE IF NOT EXISTS Nauczyciele_zloczenia (
    Id_zloczenia_klas INTEGER PRIMARY KEY NOT NULL,
    Id_klasy INTEGER NOT NULL,
    Id_nauczyciela INTEGER NOT NULL,
    czy_zaznaczona INTEGER NOT NULL,
    Id_grupy INTEGER NOT NULL,
    FOREIGN KEY (Id_Klasy) REFERENCES Klasy(Id_Klasy),
    FOREIGN KEY (Id_Nauczyciela) REFERENCES Nauczyciele(Id_Nauczyciela)
);

CREATE TABLE IF NOT EXISTS Wykluczenia (
    Id_Wykluczenia INTEGER PRIMARY KEY NOT NULL,
    Id_Nauczyciela INTEGER NOT NULL,
    Id_klikniecia INTEGER NOT NULL,
    Dzien INTEGER NOT NULL,
    Godzina INTEGER NOT NULL,
    FOREIGN KEY (Id_Nauczyciela) REFERENCES Nauczyciele(Id_Nauczyciela)
    );

CREATE TABLE IF NOT EXISTS Wykluczenia_dnia (
    Id_Wykluczenia_dnia INTEGER PRIMARY KEY NOT NULL,
    Id_Nauczyciela INTEGER NOT NULL,
    Id_klikniecia_dnia INTEGER NOT NULL,
    Dzien_caly INTEGER NOT NULL,
    FOREIGN KEY (Id_Nauczyciela) REFERENCES Nauczyciele(Id_Nauczyciela)
    );

CREATE TABLE IF NOT EXISTS Zloczenia_lekcji (
    Id_zloczenia INTEGER PRIMARY KEY NOT NULL,
    Id_Klasy INTEGER NOT NULL,
    Id_zlocz INTEGER NOT NULL,
    Id_Przedmiotu_1 INTEGER,
    Id_Przedmiotu_2 INTEGER,
    Id_Przedmiotu_3 INTEGER,
    FOREIGN KEY (Id_Klasy) REFERENCES Klasy(Id_Klasy),
    FOREIGN KEY (Id_Przedmiotu_1) REFERENCES Przedmioty(Id_Przedmiotu),
    FOREIGN KEY (Id_Przedmiotu_2) REFERENCES Przedmioty(Id_Przedmiotu),
    FOREIGN KEY (Id_Przedmiotu_3) REFERENCES Przedmioty(Id_Przedmiotu)
);

CREATE TABLE IF NOT EXISTS loczenia_grup (
    Id_loczenia_grup INTEGER PRIMARY KEY NOT NULL,
    Id_klasy INTEGER NOT NULL,
    Id_Nauczyciela INTEGER NOT NULL,
    czy_loczona BOOLEAN NOT NULL,
    ilosc_godzin INTEGER NOT NULL,
    FOREIGN KEY (Id_Nauczyciela) REFERENCES Nauczyciele(Id_Nauczyciela)
    FOREIGN KEY (Id_klasy) REFERENCES klasy(Id_klasy)
    );

