PRAGMA foreign_keys = ON; -- Włączenie obsługi kluczy obcych

create table if not exists hasla (
    Id_Hasla INTEGER PRIMARY KEY NOT NULL,
    login text not null,
    haslo text not null
);

create table if not exists bazy (
    Id_wyszukania INTEGER PRIMARY KEY NOT NULL,
    Id_Hasla INTEGER NOT NULL,
    nazwa text not null,
    FOREIGN KEY (Id_Hasla) REFERENCES hasla(Id_Hasla)
)