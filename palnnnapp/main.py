from os.path import isdevdrive
import customtkinter as ctk
import tkinter as tk
import pandas as pd
import sqlite3
import os
from customtkinter import CTkScrollableFrame, CTkButton, CTkLabel, CTkEntry


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

poloczenie = sqlite3.connect("logowanie.db")
cursor = poloczenie.cursor()

cursor.execute("PRAGMA foreign_keys = ON;")

with open("loginy_schemat.sql", "r", encoding="utf-8") as file:
    cursor.executescript(file.read())

poloczenie.commit()
poloczenie.close()

print("Baza danych została zainicjalizowana!")


def pobierz_dane_uniwersalnie(polecenie, baza):
    conn = sqlite3.connect(f"{baza}.sqlite")
    cursor = conn.cursor()
    cursor.execute(str(polecenie))
    users = cursor.fetchall()
    conn.close()
    return users

def liczby_danych_uniwersalne(polecenie, baza):
    conn = sqlite3.connect(f"{baza}.sqlite")
    cursor = conn.cursor()
    cursor.execute(polecenie)
    users = cursor.fetchone()[0]
    conn.close()
    return users


# Logowanie
class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success, show_register):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.show_register = show_register

        ctk.CTkLabel(self, text="Zaloguj się", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Login")
        self.username_entry.pack(pady=5)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Hasło", show="*")
        self.password_entry.pack(pady=5)

        ctk.CTkButton(self, text="Zaloguj", command=self.check_login).pack(pady=10)

        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.pack()

        ctk.CTkButton(self, text="Zarejestruj się", command=self.show_register).pack(pady=(10, 5))

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "admin" and password == "1234":
            self.on_login_success()
        else:
            self.error_label.configure(text="Nieprawidłowy login lub hasło")

class RegisterView(ctk.CTkFrame):
    def __init__(self, master, show_login):
        super().__init__(master)
        self.show_login = show_login

        ctk.CTkLabel(self, text="Zarejestruj się", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Nazwa użytkownika")
        self.username_entry.pack(pady=5)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Hasło", show="*")
        self.password_entry.pack(pady=5)

        self.repeat_password_entry = ctk.CTkEntry(self, placeholder_text="Powtórz hasło", show="*")
        self.repeat_password_entry.pack(pady=5)

        ctk.CTkButton(self, text="Zarejestruj (niedziała)", command=self.fake_register).pack(pady=10)

        ctk.CTkButton(self, text="← Wróć do logowania", command=self.show_login).pack(pady=10)

    def fake_register(self):
        print("Tu będzie logika rejestracji")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Panel Aplikacji")
        self.geometry("800x500")
        self.minsize(600, 400)

        self.database_buttons = []
        self.sidebar = None
        self.main_view = None
        self.current_view = None

        self.init_main_ui()



    def init_main_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_rowconfigure(99, weight=1)

        ctk.CTkLabel(self.sidebar, text="MojeApp", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=10, pady=(20, 10))

        ctk.CTkButton(self.sidebar, text="➕ Dodaj bazę danych", command=self.prompt_new_database).grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew")

        self.refresh_database_buttons()

        self.main_view = ctk.CTkFrame(self)
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.show_dashboard()

    def zapisz(self, polecenie):
        conn = sqlite3.connect("logowanie.db")
        cursor = conn.cursor()
        cursor.execute(str(polecenie))
        conn.commit()
        conn.close()

    def prompt_new_database(self):
        popup = ctk.CTkInputDialog(title="Nowa baza danych", text="Podaj nazwę bazy:")
        db_name = popup.get_input()
        #test
        logged = 1
        if db_name:
            file_name = f"{db_name}.sqlite"
            if not os.path.exists(file_name):
                sqlite3.connect(file_name).close()
                self.zapisz(f"insert into bazy(id_hasla, nazwa) values({logged}, '{db_name}.sqlite')")
            self.refresh_database_buttons()

    def pobierz_dane_uniwersalnie(self, polecenie):
        conn = sqlite3.connect("logowanie.db")
        cursor = conn.cursor()
        cursor.execute(str(polecenie))
        users = cursor.fetchall()
        conn.close()
        return users

    def refresh_database_buttons(self):
        for btn in self.database_buttons:
            btn.destroy()
        self.database_buttons.clear()

        logged = 1
        nazwy_baz = self.pobierz_dane_uniwersalnie(f"select nazwa from bazy where Id_hasla = {logged}")
        nazwy_baz_reforme = [row[0] for row in nazwy_baz]

        row = 2
        for file in os.listdir():
            if file.endswith(".sqlite") and file in nazwy_baz_reforme:
                db_name = os.path.splitext(file)[0]
                btn = ctk.CTkButton(self.sidebar, text=db_name, command=lambda name=db_name: self.enter_database_mode(name))
                btn.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
                self.database_buttons.append(btn)
                row += 1

        ust_button = ctk.CTkButton(self.sidebar, text="Ustawienia", fg_color="gray", hover_color="#006600", command=self.ustawienia_u)
        ust_button.grid(row=row, column=0, padx=10, pady=10, sticky="ew")
        row += 1

        logout_button = ctk.CTkButton(self.sidebar, text="Wyloguj", fg_color="red", hover_color="#cc0000", command=self.logout)
        logout_button.grid(row=row, column=0, padx=10, pady=20, sticky="ew")

    def enter_database_mode(self, db_name):
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        poloczenie = sqlite3.connect(f"{db_name}.sqlite")
        cursor = poloczenie.cursor()

        cursor.execute("PRAGMA foreign_keys = ON;")

        with open("dane_schemat.sql", "r", encoding="utf-8") as file:
            cursor.executescript(file.read())

        poloczenie.commit()
        poloczenie.close()

        print("Baza danych została zainicjalizowana!")

        ctk.CTkLabel(self.sidebar, text=f"Baza: {db_name}", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=(20, 10))

        ctk.CTkButton(self.sidebar, text="Nauczyciele", command=lambda: self.nauczyciele_u(db_name)).grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(self.sidebar, text="Klasy", command=lambda: self.klasy_u(db_name)).grid(row=2, column=0,padx=10, pady=10,sticky="ew")
        ctk.CTkButton(self.sidebar, text="przedmioty", command=lambda: self.przedmioty_u(db_name)).grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(self.sidebar, text="przypisanie", command=lambda: self.przypisanie_u(self.sidebar, db_name)).grid(row=4, column=0,padx=10, pady=10,sticky="ew")
        ctk.CTkButton(self.sidebar, text="Dzielenia", command=lambda: self.dzielenia_u(self.sidebar, db_name)).grid(row=5, column=0,padx=10, pady=10,sticky="ew")
        ctk.CTkButton(self.sidebar, text="Wykluczenia", command=lambda: self.wykluczenia_u(self.sidebar, db_name)).grid(row=6, column=0,padx=10, pady=10,sticky="ew")
        ctk.CTkButton(self.sidebar, text="Zloczenia", command=lambda: self.zloczenia_u(self.sidebar, db_name)).grid(row=7, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(self.sidebar, text="← Wróć do baz", command=self.back_to_database_list, fg_color="purple").grid(row=8, column=0, padx=10, pady=10, sticky="ew" )
        ctk.CTkLabel(self.main_view, text=f"Pracujesz na bazie: {db_name}.sqlite").pack(pady=10)

    def back_to_database_list(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        self.init_main_ui()

    def logout(self):
        self.destroy()

    def clear_main_view(self):
        for widget in self.main_view.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_main_view()
        ctk.CTkLabel(self.main_view, text="Witaj w aplikacji!").pack(pady=20)

    def nauczyciele_u(self, db_name):
        self.clear_main_view()
        self.current_view = Nauczyciele(self.main_view, db_name)
        self.current_view.pack(fill="both", expand=True)

    def klasy_u(self, db_name):
        self.clear_main_view()
        self.current_view = Klasy(self.main_view, db_name)
        self.current_view.pack(fill="both", expand=True)

    def przedmioty_u(self, db_name):
        self.clear_main_view()
        self.current_view = Przedmioty(self.main_view, db_name)
        self.current_view.pack(fill="both", expand=True)

    def przypisanie_u(self, sidebar, db_name):
        self.clear_main_view()
        self.current_view = Przypisanie(self.main_view, sidebar, db_name)
        self.current_view.pack(fill="both", expand=True)

    def dzielenia_u(self, sidebar, db_name):
        self.clear_main_view()
        self.current_view = Dzielenia(self.main_view, sidebar, db_name)
        self.current_view.pack(fill="both", expand=True)

    def wykluczenia_u(self, sidebar, db_name):
        self.clear_main_view()
        self.current_view = Wykluczenia(self.main_view, sidebar, db_name)
        self.current_view.pack(fill="both", expand=True)

    def zloczenia_u(self, sidebar, db_name):
        self.clear_main_view()
        self.current_view = ZloczeniaG(self.main_view, sidebar, db_name)
        self.current_view.pack(fill="both", expand=True)

    def ustawienia_u(self):
        self.clear_main_view()
        self.current_view = Ustawienia(self.main_view)
        self.current_view.pack(fill="both", expand=True)

class DashboardView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Panel główny", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        ctk.CTkButton(self, text="Akcja").pack(pady=10)

class Ustawienia(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        ctk.CTkLabel(self, text="Ustawienia aplikacji", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)

        ctk.CTkLabel(self, text="Wybierz motyw:").pack(pady=(10, 5))

        self.motyw_var = ctk.StringVar(value=ctk.get_appearance_mode())
        self.motyw_menu = ctk.CTkOptionMenu(
            self, values=["System", "Light", "Dark"],
            variable=self.motyw_var,
            command=self.zmien_motyw
        )
        self.motyw_menu.pack(pady=10)

    def zmien_motyw(self, wybor):
        ctk.set_appearance_mode(wybor)

class Dzielenia(ctk.CTkFrame):
    def __init__(self, master, sidebar, db_name):
        super().__init__(master)
        self.db_name = db_name
        self.sidebar = sidebar
        self.main = master

        for widget in self.sidebar.winfo_children():
            widget.destroy()

        self.scrollbar_side = CTkScrollableFrame(self.sidebar)
        self.scrollbar_side.pack(fill="both", expand=True)

        ctk.CTkLabel(self.scrollbar_side, text=f"Baza: {db_name}", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=(20, 10))

        id_k = pobierz_dane_uniwersalnie("select id_klasy, nazwa from klasy", self.db_name)
        print(id_k)
        row = 1
        for index, (id_n, nazwa) in enumerate(id_k, start=1):
            ctk.CTkButton(self.scrollbar_side, text=f"{nazwa}", command=lambda id1 = id_n: self.przypisanie_klasy(id1)).grid(row=row, column=0, padx=10, pady=10, sticky="ew")
            row += 1
        ctk.CTkButton(self.scrollbar_side, text="← Wróć do baz", command=self.back_to_menu, fg_color="purple").grid(row=row, column=0, padx=10, pady=10, sticky="ew")

    def back_to_menu(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        app.enter_database_mode(self.db_name)

    def clear_main_view(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def przypisanie_klasy(self, id_naucz):
        self.clear_main_view()
        self.current_view = KonstruktorPodzialu(self.main, self.db_name, id_naucz)
        self.current_view.pack(fill="both", expand=True)

class KonstruktorPodzialu(ctk.CTkFrame):
    def __init__(self, master, db_name, id_n):
        super().__init__(master)
        self.db_name = db_name
        self.id_n = id_n
        self.przypisania_widgets = []
        self.entry_przedmioty_list = []
        self.entry_nauczyciele_list = []
        self.entry_bool_list = []
        self.bool_list = []
        self.update_btn_list = []
        self.wartosc_gr1 = []
        self.wartosc_gr2 = []
        self.update_gr_list = []
        self.opis_ogl = []
        self.opis_gr1 = []
        self.opis_gr2 = []

        ctk.CTkLabel(self, text=f"klasa: {liczby_danych_uniwersalne(f"select nazwa from klasy where id_klasy = {self.id_n}", self.db_name)}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        CTkButton(self, text="dodaj podział", command=lambda: self.dodaj_podzial()).pack(pady=10)

        self.scrollbar = CTkScrollableFrame(self)
        self.scrollbar.pack(fill="both", expand=True)

        lista_przedmiotow = pobierz_dane_uniwersalnie("select nazwa_p from przedmioty", self.db_name)
        self.lista_przedmiotow_reforme = [row[0] for row in lista_przedmiotow]

        self.lista_bool = ["Tak", "Nie"]

        podzial = pobierz_dane_uniwersalnie(f"select id_dzielenia, id_przedmiotu, id_nauczyciela, czy_dzielona, godzina from dzielenia where id_klasy = {self.id_n}", self.db_name)

        for index, (id_d, id_p, id_n, czy_dziel, godz) in enumerate(podzial, start=1):
            row_frame = ctk.CTkFrame(self.scrollbar)
            row_frame.pack(fill="x", pady=2)

            lista_nauczycieli = pobierz_dane_uniwersalnie(f"select nazwisko from nauczyciele join przypisanie on nauczyciele.id_nauczyciela = przypisanie.id_nauczyciela where id_przedmiotu = {id_p}", self.db_name)
            lista_nauczycieli_reforme = [row[0] for row in lista_nauczycieli]

            label = CTkLabel(row_frame, text=f"przedmiot nr: {index}   ")
            label.pack(pady=10, side="left")

            podstawowa_wartosc_p = tk.StringVar(value=liczby_danych_uniwersalne(f"select nazwa_p from przedmioty where id_przedmiotu = {id_p}", self.db_name))
            podstawowa_wartosc_n = tk.StringVar(value=liczby_danych_uniwersalne(f"select nazwisko from nauczyciele where id_nauczyciela = {id_n}", self.db_name))
            if czy_dziel:
                wartosc = "Tak"
            else:
                wartosc = "Nie"
            podstawowa_wartosc_w = tk.StringVar(value=wartosc)

            lista_p = ctk.CTkComboBox(row_frame, values=self.lista_przedmiotow_reforme, variable=podstawowa_wartosc_p, command=lambda _, p_id = id_d: self.aktualizuj_podzial(p_id))
            lista_p.pack(pady=10, padx=5, side="left")
            CTkLabel(row_frame, text="nauczyciel: ").pack(side="left")
            lista_n = ctk.CTkComboBox(row_frame, values=lista_nauczycieli_reforme, variable=podstawowa_wartosc_n, command=lambda _, p_id = id_d: self.aktualizuj_podzial(p_id))
            lista_n.pack(pady=10, padx=5, side="left")
            CTkLabel(row_frame, text="czy jest dzielona na grupy?: ").pack(side="left")
            lista_w = ctk.CTkComboBox(row_frame, values=self.lista_bool, variable=podstawowa_wartosc_w, command=lambda _, p_id = id_d, f = row_frame: (self.aktualizuj_podzial(p_id), self.edycja_godzin(p_id, f)))
            lista_w.pack(pady=10, padx=5, side="left")

            btn_usun = ctk.CTkButton(row_frame, text="x", font=("Arial", 12, "bold"), width=10, command=lambda f=row_frame, id1=id_d: self.usun_podzial(id1, f))
            btn_usun.pack(side="right", padx=5)

            self.entry_przedmioty_list.append({"id": id_d, "entry": lista_p})
            self.entry_nauczyciele_list.append({"id": id_d, "entry": lista_n})
            self.entry_bool_list.append({"id": id_d, "entry": lista_w})
            self.przypisania_widgets.append({"frame": row_frame, "id": id_d, "label": label})

            self.edycja_godzin(id_d, row_frame)

    def dodaj_podzial(self):
        nowe_id_dzielenia = liczby_danych_uniwersalne(f"SELECT COALESCE(MAX(id_dzielenia), 0) FROM dzielenia WHERE id_klasy = {self.id_n}", self.db_name) + 1

        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO dzielenia(id_dzielenia, id_klasy, id_przedmiotu, id_nauczyciela, czy_dzielona, godzina, gr1, gr2, gr3) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",(nowe_id_dzielenia ,self.id_n, 1, 1, 0, 0, 0, 0, 0))
            conn.commit()
            print("Dane dodane pomyślnie.")
        except sqlite3.Error as e:
            print("Błąd podczas dodawania danych:", e)
            return
        finally:
            conn.close()

        row_frame = ctk.CTkFrame(self.scrollbar)
        row_frame.pack(fill="x", pady=2)

        label = CTkLabel(row_frame, text=f"przypisanie nr: {len(self.przypisania_widgets) + 1}")
        label.pack(pady=10, side="left")

        lista_nauczycieli = pobierz_dane_uniwersalnie(f"select nazwisko from nauczyciele", self.db_name)
        lista_nauczycieli_reforme = [row[0] for row in lista_nauczycieli]

        CTkLabel(row_frame, text="przedmiot: ").pack(side="left")
        lista_p = ctk.CTkComboBox(row_frame, values=self.lista_przedmiotow_reforme, command=lambda _, dzielenia_id=nowe_id_dzielenia: self.aktualizuj_podzial(dzielenia_id))
        lista_p.pack(pady=10, padx=5, side="left")
        CTkLabel(row_frame, text="nauczyciel: ").pack(side="left")
        lista_n = ctk.CTkComboBox(row_frame, values=lista_nauczycieli_reforme, command=lambda _, dzielenia_id=nowe_id_dzielenia: self.aktualizuj_podzial(dzielenia_id))
        lista_n.pack(pady=10, padx=5, side="left")
        nie = tk.StringVar(value="Nie")
        CTkLabel(row_frame, text="czy jest dzielona na grupy?: ").pack(side="left")
        lista_w = ctk.CTkComboBox(row_frame, values=self.lista_bool, variable=nie, command=lambda _, f=row_frame, dzielenia_id=nowe_id_dzielenia: (self.aktualizuj_podzial(dzielenia_id), self.edycja_godzin(dzielenia_id, f)))
        lista_w.pack(pady=10, padx=5, side="left")

        btn_usun = ctk.CTkButton(row_frame, text="x", font=("Arial", 12, "bold"), width=10, command=lambda f=row_frame, id1=nowe_id_dzielenia: self.usun_podzial(id1, f))
        btn_usun.pack(side="right", padx=5)

        self.entry_przedmioty_list.append({"id": nowe_id_dzielenia, "entry": lista_p})
        self.entry_nauczyciele_list.append({"id": nowe_id_dzielenia, "entry": lista_n})
        self.entry_bool_list.append({"id": nowe_id_dzielenia, "entry": lista_w})
        self.przypisania_widgets.append({"frame": row_frame, "id": nowe_id_dzielenia, "label": label})
        self.edycja_godzin(nowe_id_dzielenia, row_frame)
        self.odswiez_numery()

    def edycja_godzin(self, id_dzielenia, frame):
        entry_w = next((e["entry"] for e in self.entry_bool_list if e["id"] == id_dzielenia), None)
        if entry_w is None:
            print(f"Nie znaleziono entry dla lekcji ID={id_dzielenia}")
            return
        stan_dziel = entry_w.get()

        if stan_dziel == "Tak":
            entry_b = next((e["entry"] for e in self.bool_list if e["id"] == id_dzielenia), None)
            entry_u = next((e["entry"] for e in self.update_btn_list if e["id"] == id_dzielenia), None)
            opis_ogl = next((e["entry"] for e in self.opis_ogl if e["id"] == id_dzielenia), None)

            if entry_b and entry_u:
                self.wyzeruj(id_dzielenia)
                entry_b.destroy()
                entry_u.destroy()
                opis_ogl.destroy()
                self.bool_list = [e for e in self.bool_list if e["id"] != id_dzielenia]
                self.update_btn_list = [e for e in self.update_btn_list if e["id"] != id_dzielenia]
                self.opis_ogl = [e for e in self.opis_ogl if e["id"] != id_dzielenia]

                print("Usunięto Entry dla id:", id_dzielenia)

            istniejev2 = any(e["id"] == id_dzielenia for e in self.wartosc_gr1)

            if not istniejev2:
                info_gr1 = ctk.CTkLabel(frame, text="gr1: ")
                info_gr1.pack(side="left")
                liczba_h_gr1 = ctk.CTkEntry(frame)
                liczba_h_gr1.insert(0, liczby_danych_uniwersalne(f"select gr1 from dzielenia where id_klasy = {self.id_n} and id_dzielenia = {id_dzielenia}", self.db_name))
                liczba_h_gr1.pack(side="left", padx=5)

                info_gr2 = ctk.CTkLabel(frame, text="gr2: ")
                info_gr2.pack(side="left")
                liczba_h_gr2 = ctk.CTkEntry(frame)
                liczba_h_gr2.insert(0, liczby_danych_uniwersalne(f"select gr2 from dzielenia where id_klasy = {self.id_n} and id_dzielenia = {id_dzielenia}", self.db_name))
                liczba_h_gr2.pack(side="left", padx=5)

                aktu_btnv2 = ctk.CTkButton(frame, text="?", font=("Arial", 12, "bold"), width=10, command=lambda id1=id_dzielenia: self.aktualizuj_gr(id1))
                aktu_btnv2.pack(side="right", padx=5)

                self.wartosc_gr1.append({"id": id_dzielenia, "entry": liczba_h_gr1})
                self.wartosc_gr2.append({"id": id_dzielenia, "entry": liczba_h_gr2})
                self.update_gr_list.append({"id": id_dzielenia, "entry": aktu_btnv2})
                self.opis_gr1.append({"id": id_dzielenia, "entry": info_gr1})
                self.opis_gr2.append({"id": id_dzielenia, "entry": info_gr2})
            else:
                print("Entry już istnieje, nic nie dodano.")

        else:
            entry_gr1 = next((e["entry"] for e in self.wartosc_gr1 if e["id"] == id_dzielenia), None)
            entry_gr2 = next((e["entry"] for e in self.wartosc_gr2 if e["id"] == id_dzielenia), None)
            entry_uv2 = next((e["entry"] for e in self.update_gr_list if e["id"] == id_dzielenia), None)
            opis_gr1 = next((e["entry"] for e in self.opis_gr1 if e["id"] == id_dzielenia), None)
            opis_gr2 = next((e["entry"] for e in self.opis_gr2 if e["id"] == id_dzielenia), None)
            if entry_gr1 and entry_gr2 and entry_uv2:
                self.wyzeruj_gr(id_dzielenia)
                entry_gr1.destroy()
                entry_gr2.destroy()
                entry_uv2.destroy()
                opis_gr1.destroy()
                opis_gr2.destroy()
                self.wartosc_gr1 = [e for e in self.wartosc_gr1 if e["id"] != id_dzielenia]
                self.wartosc_gr2 = [e for e in self.wartosc_gr2 if e["id"] != id_dzielenia]
                self.update_gr_list = [e for e in self.update_gr_list if e["id"] != id_dzielenia]
                self.opis_gr1 = [e for e in self.opis_gr1 if e["id"] != id_dzielenia]
                self.opis_gr2 = [e for e in self.opis_gr2 if e["id"] != id_dzielenia]
                print("Usunięto Entry dla id:", id_dzielenia)

            istnieje = any(e["id"] == id_dzielenia for e in self.bool_list)
            if not istnieje:
                info_ogl = ctk.CTkLabel(frame, text="liczba godzin: ")
                info_ogl.pack(side="left")
                liczba_h = ctk.CTkEntry(frame)
                liczba_h.insert(0, liczby_danych_uniwersalne(f"select godzina from dzielenia where id_klasy = {self.id_n} and id_dzielenia = {id_dzielenia}", self.db_name))
                liczba_h.pack(side="left", padx=5)

                aktu_btn = ctk.CTkButton(frame, text="?", font=("Arial", 12, "bold"), width=10, command=lambda id1=id_dzielenia: self.aktualizuj_godz(id1))
                aktu_btn.pack(side="right", padx=5)
                self.bool_list.append({"id": id_dzielenia, "entry": liczba_h})
                self.update_btn_list.append({"id": id_dzielenia, "entry": aktu_btn})
                self.opis_ogl.append({"id": id_dzielenia, "entry": info_ogl})
                print("Dodano Entry dla id:", id_dzielenia)
            else:
                print("Entry już istnieje, nic nie dodano.")

    def wyzeruj(self, id_dzielenia):
        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("update dzielenia set godzina = ? where id_klasy = ? and id_dzielenia = ?",(0, self.id_n, id_dzielenia))
            conn.commit()
            print("Dane edytowane pomyślnie.")

        except sqlite3.Error as e:
            print("Błąd podczas edycji danych:", e)
        finally:
            conn.close()

    def wyzeruj_gr(self, id_dzielenia):
        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("update dzielenia set gr1 = ?, gr2 = ? where id_klasy = ? and id_dzielenia = ?",(0, 0, self.id_n, id_dzielenia))
            conn.commit()
            print("Dane edytowane pomyślnie.")

        except sqlite3.Error as e:
            print("Błąd podczas edycji danych:", e)
        finally:
            conn.close()

    def aktualizuj_godz(self, id_dzielenia):
        entry_g = next((e["entry"] for e in self.bool_list if e["id"] == id_dzielenia), None)
        if entry_g is None:
            print(f"Nie znaleziono entry dla lekcji ID={id_dzielenia}")
            return

        nazwa_g = entry_g.get()

        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("update dzielenia set godzina = ? where id_klasy = ? and id_dzielenia = ?", (nazwa_g, self.id_n, id_dzielenia))
            conn.commit()
            print("Dane edytowane pomyślnie.")

        except sqlite3.Error as e:
            print("Błąd podczas edycji danych:", e)
        finally:
            conn.close()

    def aktualizuj_gr(self, id_dzielenia):
        entry_gr1 = next((e["entry"] for e in self.wartosc_gr1 if e["id"] == id_dzielenia), None)
        entry_gr2 = next((e["entry"] for e in self.wartosc_gr2 if e["id"] == id_dzielenia), None)

        godzina_gr1 = entry_gr1.get()
        godzina_gr2 = entry_gr2.get()

        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("update dzielenia set gr1 = ?, gr2 = ? where id_klasy = ? and id_dzielenia = ?",(godzina_gr1, godzina_gr2, self.id_n, id_dzielenia))
            conn.commit()
            print("Dane edytowane pomyślnie.")

        except sqlite3.Error as e:
            print("Błąd podczas edycji danych:", e)
        finally:
            conn.close()

    def odswiez_numery(self):
        for i, nauczyciel in enumerate(self.przypisania_widgets, start=1):
            nauczyciel["label"].configure(text=f"przypisanie nr: {i}    ")
            print(self.przypisania_widgets)
            print(self.entry_przedmioty_list)

    def aktualizuj_podzial(self, id_dzielenia):
        print(f"dzielenie ID={id_dzielenia} edytowane")
        entry_p = next((e["entry"] for e in self.entry_przedmioty_list if e["id"] == id_dzielenia), None)
        entry_n = next((e["entry"] for e in self.entry_nauczyciele_list if e["id"] == id_dzielenia), None)
        entry_w = next((e["entry"] for e in self.entry_bool_list if e["id"] == id_dzielenia), None)
        if entry_p is None or entry_n is None or entry_w is None:
            print(f"Nie znaleziono entry dla lekcji ID={id_dzielenia}")
            return

        nazwa_p = entry_p.get()
        nazwa_n = entry_n.get()
        nazwa_w = entry_w.get()

        nazwa_db = liczby_danych_uniwersalne(f"select id_przedmiotu from dzielenia where id_dzielenia = {id_dzielenia} and id_klasy = {self.id_n}", self.db_name)

        if nazwa_p != liczby_danych_uniwersalne(f"select nazwa_p from przedmioty where id_przedmiotu = {nazwa_db}", self.db_name):
            potrzeba = liczby_danych_uniwersalne(f"select id_przedmiotu from przedmioty where nazwa_p = '{nazwa_p}'",self.db_name)
            potrzebav2 = liczby_danych_uniwersalne(f"select id_nauczyciela from przypisanie where id_przedmiotu = {potrzeba}", self.db_name)
            entry_n.set(liczby_danych_uniwersalne(f"select nazwisko from nauczyciele where id_nauczyciela = {potrzebav2}", self.db_name))
            nazwa_n = liczby_danych_uniwersalne(f"select nazwisko from nauczyciele where id_nauczyciela = {potrzebav2}", self.db_name)

        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id_przedmiotu FROM przedmioty WHERE nazwa_p = ?", (nazwa_p,))
            wynik_p = cursor.fetchone()
            cursor.execute("SELECT id_nauczyciela FROM nauczyciele WHERE nazwisko = ?", (nazwa_n,))
            wynik_n = cursor.fetchone()
            if nazwa_w == "Tak":
                wynik_w = 1
            else:
                wynik_w = 0
            if wynik_p:
                id_przedmiotu = wynik_p[0]
                cursor.execute("UPDATE dzielenia SET id_przedmiotu = ? WHERE id_klasy = ? AND id_dzielenia = ?",(id_przedmiotu, self.id_n, id_dzielenia))
                conn.commit()
                lista_nauczycieli = pobierz_dane_uniwersalnie(f"select nazwisko from nauczyciele join przypisanie on nauczyciele.id_nauczyciela = przypisanie.id_nauczyciela where id_przedmiotu = {id_przedmiotu}", self.db_name)
                lista_nauczycieli_reforme = [row[0] for row in lista_nauczycieli]
                entry_n.configure(values=lista_nauczycieli_reforme)
                print("Dane edytowane pomyślnie.")
            else:
                print(f"Nie znaleziono przedmiotu o nazwie: {nazwa_p}")
            if wynik_n:
                id_nauczy = wynik_n[0]
                cursor.execute("UPDATE dzielenia SET id_nauczyciela = ? WHERE id_klasy = ? AND id_dzielenia = ?",(id_nauczy, self.id_n, id_dzielenia))
                conn.commit()
                print("Dane edytowane pomyślnie.")
            else:
                print(f"Nie znaleziono przedmiotu o nazwie: {nazwa_n}")

            cursor.execute("UPDATE dzielenia SET czy_dzielona = ? WHERE id_klasy = ? AND id_dzielenia = ?",(wynik_w, self.id_n, id_dzielenia))
            conn.commit()
            print("Dane edytowane pomyślnie.")

        except sqlite3.Error as e:
            print("Błąd podczas edycji danych:", e)
        finally:
            conn.close()

    def usun_podzial(self, id_lekcji, frame):
        print(f"Usuwanie przedmiotu ID={self.id_n}")
        frame.destroy()

        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM przypisanie WHERE Id_nauczyciela = ? and id_lekcji = ?", (self.id_n, id_lekcji))
            conn.commit()
        except sqlite3.Error as e:
            print("Błąd podczas usuwania:", e)
        finally:
            conn.close()

        self.entry_przedmioty_list = [w for w in self.entry_przedmioty_list if w["id"] != id_lekcji]
        self.entry_przedmioty_list = [e for e in self.entry_przedmioty_list if e["id"] != id_lekcji]
        self.odswiez_numery()
        print(self.entry_przedmioty_list)
        print(self.entry_przedmioty_list)

class ZloczeniaG(ctk.CTkFrame):
    def __init__(self, master, sidebar, db_name):
        super().__init__(master)
        self.db_name = db_name
        self.sidebar = sidebar
        self.main = master

        for widget in self.sidebar.winfo_children():
            widget.destroy()

        self.scrollbar_side = CTkScrollableFrame(self.sidebar)
        self.scrollbar_side.pack(fill="both", expand=True)

        ctk.CTkLabel(self.scrollbar_side, text=f"Baza: {db_name}", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=(20, 10))

        id_k = pobierz_dane_uniwersalnie("select id_klasy, nazwa from klasy", self.db_name)
        print(id_k)
        row = 1
        for index, (id_n, nazwa) in enumerate(id_k, start=1):
            ctk.CTkButton(self.scrollbar_side, text=f"{nazwa}", command=lambda id1 = id_n: self.przypisanie_klasy(id1)).grid(row=row, column=0, padx=10, pady=10, sticky="ew")
            row += 1
        ctk.CTkButton(self.scrollbar_side, text="← Wróć do baz", command=self.back_to_menu, fg_color="purple").grid(row=row, column=0, padx=10, pady=10, sticky="ew")

    def back_to_menu(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        app.enter_database_mode(self.db_name)

    def clear_main_view(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def przypisanie_klasy(self, id_naucz):
        self.clear_main_view()
        self.current_view = KZloczenG(self.main, self.db_name, id_naucz)
        self.current_view.pack(fill="both", expand=True)

class Wykluczenia(ctk.CTkFrame):
    def __init__(self, master, sidebar, db_name):
        super().__init__(master)
        self.db_name = db_name
        self.sidebar = sidebar
        self.main = master

        for widget in self.sidebar.winfo_children():
            widget.destroy()

        self.scrollbar_side = CTkScrollableFrame(self.sidebar)
        self.scrollbar_side.pack(fill="both", expand=True)

        ctk.CTkLabel(self.scrollbar_side, text=f"Baza: {db_name}", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=(20, 10))

        id = pobierz_dane_uniwersalnie("select id_nauczyciela, nazwisko from nauczyciele", self.db_name)
        print(id)
        row = 1
        for index, (id_n, nazwisko) in enumerate(id, start=1):
            ctk.CTkButton(self.scrollbar_side, text=f"{nazwisko}", command=lambda id1 = id_n: self.przypisanie_nauczyciela(id1)).grid(row=row, column=0, padx=10, pady=10, sticky="ew")
            row += 1
        ctk.CTkButton(self.scrollbar_side, text="← Wróć do baz", command=self.back_to_menu, fg_color="purple").grid(row=row, column=0, padx=10, pady=10, sticky="ew")

    def back_to_menu(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        app.enter_database_mode(self.db_name)

    def clear_main_view(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def przypisanie_nauczyciela(self, id_naucz):
        self.clear_main_view()
        self.current_view = KWykluczen(self.main, self.db_name, id_naucz)
        self.current_view.pack(fill="both", expand=True)

class KZloczenG(ctk.CTkFrame):
    def __init__(self, master, db_name, id_n):
        super().__init__(master)
        self.db_name = db_name
        self.id_n = id_n
        self.entry_p1_list = []
        self.entry_p2_list = []
        self.entry_p3_list = []
        self.zloczenia_l_widgets = []

        ctk.CTkLabel(self, text=f"Klasa: {liczby_danych_uniwersalne(f"select nazwa from klasy where id_klasy = {self.id_n}", self.db_name)}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        self.scrollbar = CTkScrollableFrame(self)
        self.scrollbar.pack(fill="both", expand=True)

        CTkButton(self.scrollbar, text="dodaj złączenie przedmiotów", command=lambda: self.dodaj_zloczeniep()).pack(pady=10)

        przedmioty = pobierz_dane_uniwersalnie(f"select przedmioty.nazwa_p from przedmioty join dzielenia on przedmioty.Id_przedmiotu = dzielenia.Id_przedmiotu where dzielenia.id_klasy = {self.id_n}", self.db_name)
        self.przedmioty_reforme = [row[0] for row in przedmioty]

        zloczenie = pobierz_dane_uniwersalnie(f"select Id_zlocz, Id_przedmiotu_1, Id_przedmiotu_2, Id_przedmiotu_3 from zloczenia_lekcji where Id_klasy = {self.id_n}", self.db_name)

        for index, (id_zlocz, Id_p1, Id_p2, Id_p3) in enumerate(zloczenie, start=1):
            row_frame = ctk.CTkFrame(self.scrollbar)
            row_frame.pack(fill="x", pady=2)

            label = CTkLabel(row_frame, text=f"złączenie nr: {index}   ")
            label.pack(pady=10, side="left")
            if liczby_danych_uniwersalne(f"select id_przedmiotu_1 from zloczenia_lekcji where id_zlocz = {id_zlocz} and id_klasy = {self.id_n}", self.db_name):
                podstawowa_wartosc_p1 = tk.StringVar(value=liczby_danych_uniwersalne(f"select nazwa_p from przedmioty join zloczenia_lekcji on przedmioty.id_przedmiotu = zloczenia_lekcji.id_przedmiotu_1 where id_zlocz = {id_zlocz} and id_klasy = {self.id_n}", self.db_name))
            else:
                podstawowa_wartosc_p1 = tk.StringVar(value=None)
            if liczby_danych_uniwersalne(f"select id_przedmiotu_2 from zloczenia_lekcji where id_zlocz = {id_zlocz} and id_klasy = {self.id_n}", self.db_name):
                podstawowa_wartosc_p2 = tk.StringVar(value=liczby_danych_uniwersalne(f"select nazwa_p from przedmioty join zloczenia_lekcji on przedmioty.id_przedmiotu = zloczenia_lekcji.id_przedmiotu_2 where id_zlocz = {id_zlocz} and id_klasy = {self.id_n}", self.db_name))
            else:
                podstawowa_wartosc_p2 = tk.StringVar(value=None)
            if liczby_danych_uniwersalne(f"select id_przedmiotu_3 from zloczenia_lekcji where id_zlocz = {id_zlocz} and id_klasy = {self.id_n}", self.db_name):
                podstawowa_wartosc_p3 = tk.StringVar(value=liczby_danych_uniwersalne(f"select nazwa_p from przedmioty join zloczenia_lekcji on przedmioty.id_przedmiotu = zloczenia_lekcji.id_przedmiotu_3 where id_zlocz = {id_zlocz} and id_klasy = {self.id_n}", self.db_name))
            else:
                podstawowa_wartosc_p3 = tk.StringVar(value=None)

            entry_p1 = ctk.CTkComboBox(row_frame, values=self.przedmioty_reforme, variable=podstawowa_wartosc_p1, command=lambda _, klikniecie_id=id_zlocz: self.aktualizuj_zloczeniap(klikniecie_id))
            entry_p1.pack(pady=10, padx=5, side="left")
            entry_p2 = ctk.CTkComboBox(row_frame, values=self.przedmioty_reforme, variable=podstawowa_wartosc_p2, command=lambda _, klikniecie_id=id_zlocz: self.aktualizuj_zloczeniap(klikniecie_id))
            entry_p2.pack(pady=10, padx=5, side="left")
            entry_p3 = ctk.CTkComboBox(row_frame, values=self.przedmioty_reforme, variable=podstawowa_wartosc_p3, command=lambda _, klikniecie_id=id_zlocz: self.aktualizuj_zloczeniap(klikniecie_id))
            entry_p3.pack(pady=10, padx=5, side="left")

            btn_usun = ctk.CTkButton(row_frame, text="x", font=("Arial", 12, "bold"), width=10, command=lambda f=row_frame, id1=id_zlocz: self.usun_zloczeniap(id1, f))
            btn_usun.pack(side="right", padx=5)

            self.entry_p1_list.append({"id": id_zlocz, "entry": entry_p1})
            self.entry_p2_list.append({"id": id_zlocz, "entry": entry_p2})
            self.entry_p3_list.append({"id": id_zlocz, "entry": entry_p3})
            self.zloczenia_l_widgets.append({"frame": row_frame, "id": id_zlocz, "label": label})

    def dodaj_zloczeniep(self):
        nowe_id_zloczenia = liczby_danych_uniwersalne(
            f"SELECT COALESCE(MAX(id_zloczenia), 0) FROM zloczenia_lekcji WHERE id_klasy = {self.id_n}", self.db_name) + 1

        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO zloczenia_lekcji(id_klasy, id_zlocz, id_przedmiotu_1, id_przedmiotu_2, id_przedmiotu_3) VALUES(?, ?, ?, ?, ?)",(self.id_n, nowe_id_zloczenia, None, None, None))
            conn.commit()
            print("Dane dodane pomyślnie.")
        except sqlite3.Error as e:
            print("Błąd podczas dodawania danych:", e)
            return
        finally:
            conn.close()

        row_frame = ctk.CTkFrame(self.scrollbar)
        row_frame.pack(fill="x", pady=2)

        label = CTkLabel(row_frame, text=f"złączenie nr: {len(self.zloczenia_l_widgets) + 1}")
        label.pack(pady=10, side="left")

        podstawowa_wartosc1 = tk.StringVar(value=None)
        podstawowa_wartosc2 = tk.StringVar(value=None)
        podstawowa_wartosc3 = tk.StringVar(value=None)

        entry_p1 = ctk.CTkComboBox(row_frame, values=self.przedmioty_reforme, variable=podstawowa_wartosc1, command=lambda _, klikniecie_id=nowe_id_zloczenia: self.aktualizuj_zloczeniap(klikniecie_id))
        entry_p1.pack(pady=10, padx=5, side="left")
        entry_p2 = ctk.CTkComboBox(row_frame, values=self.przedmioty_reforme, variable=podstawowa_wartosc2, command=lambda _, klikniecie_id=nowe_id_zloczenia: self.aktualizuj_zloczeniap(klikniecie_id))
        entry_p2.pack(pady=10, padx=5, side="left")
        entry_p3 = ctk.CTkComboBox(row_frame, values=self.przedmioty_reforme, variable=podstawowa_wartosc3, command=lambda _, klikniecie_id=nowe_id_zloczenia: self.aktualizuj_zloczeniap(klikniecie_id))
        entry_p3.pack(pady=10, padx=5, side="left")

        btn_usun = ctk.CTkButton(row_frame, text="x", font=("Arial", 12, "bold"), width=10, command=lambda f=row_frame, id1=nowe_id_zloczenia: self.usun_zloczeniap(id1, f))
        btn_usun.pack(side="right", padx=5)

        self.entry_p1_list.append({"id": nowe_id_zloczenia, "entry": entry_p1})
        self.entry_p2_list.append({"id": nowe_id_zloczenia, "entry": entry_p2})
        self.entry_p3_list.append({"id": nowe_id_zloczenia, "entry": entry_p3})
        self.zloczenia_l_widgets.append({"frame": row_frame, "id": nowe_id_zloczenia, "label": label})
        self.odswiez_numery()

    def odswiez_numery(self):
        for i, nauczyciel in enumerate(self.zloczenia_l_widgets, start=1):
            nauczyciel["label"].configure(text=f"wykluczenie nr: {i}    ")
            print(self.zloczenia_l_widgets)
            print(self.entry_p1_list)
            print(self.entry_p2_list)
            print(self.entry_p3_list)

    def aktualizuj_zloczeniap(self, id_klikniecia):
        print(f"wykluczenie ID={id_klikniecia} edytowany")
        entry_p1 = next((e["entry"] for e in self.entry_p1_list if e["id"] == id_klikniecia), None)
        entry_p2 = next((e["entry"] for e in self.entry_p2_list if e["id"] == id_klikniecia), None)
        entry_p3 = next((e["entry"] for e in self.entry_p3_list if e["id"] == id_klikniecia), None)
        if entry_p1 is None and entry_p2 is None and entry_p3 is None:
            print(f"Nie znaleziono entry dla złączenia ID={id_klikniecia}")
            return

        p1 = entry_p1.get()
        p2 = entry_p2.get()
        p3 = entry_p3.get()

        if p1:
            try:
                id_p1 = liczby_danych_uniwersalne(
                    f"SELECT id_przedmiotu FROM przedmioty WHERE nazwa_p = '{p1}'",
                    self.db_name
                )
            except TypeError:
                print(f"Nie znaleziono przedmiotu o nazwie '{p1}' – przerwano.")
                id_p1 = None
        else:
            id_p1 = None
        if p2:
            try:
                id_p2 = liczby_danych_uniwersalne(
                    f"SELECT id_przedmiotu FROM przedmioty WHERE nazwa_p = '{p2}'",
                    self.db_name
                )
            except TypeError:
                print(f"Nie znaleziono przedmiotu o nazwie '{p2}' – przerwano.")
                id_p2 = None
        else:
            id_p2 = None
        if p3:
            try:
                id_p3 = liczby_danych_uniwersalne(
                    f"SELECT id_przedmiotu FROM przedmioty WHERE nazwa_p = '{p3}'",
                    self.db_name
                )
            except TypeError:
                print(f"Nie znaleziono przedmiotu o nazwie '{p3}' – przerwano.")
                id_p3 = None
        else:
            id_p3 = None
        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE zloczenia_lekcji SET id_przedmiotu_1 = ?, id_przedmiotu_2 = ?, id_przedmiotu_3 = ? WHERE id_klasy = ? AND id_zlocz = ?",(id_p1, id_p2, id_p3, self.id_n, id_klikniecia))
            conn.commit()
            print("Dane edytowane pomyślnie.")
        except sqlite3.Error as e:
            print("Błąd podczas edycji danych:", e)
        finally:
            conn.close()

    def usun_zloczeniap(self, id_klikniecia, frame):
        print(f"Usuwanie zloczenia ID={self.id_n}")
        frame.destroy()

        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM zloczenia_lekcji WHERE Id_klasy = ? and id_zlocz = ?", (self.id_n, id_klikniecia))
            conn.commit()
        except sqlite3.Error as e:
            print("Błąd podczas usuwania:", e)
        finally:
            conn.close()

        self.zloczenia_l_widgets = [w for w in self.zloczenia_l_widgets if w["id"] != id_klikniecia]
        self.entry_p1_list = [e for e in self.entry_p1_list if e["id"] != id_klikniecia]
        self.entry_p2_list = [e for e in self.entry_p2_list if e["id"] != id_klikniecia]
        self.entry_p3_list = [e for e in self.entry_p3_list if e["id"] != id_klikniecia]
        self.odswiez_numery()
        print(self.zloczenia_l_widgets)
        print(self.entry_p1_list)
        print(self.entry_p2_list)
        print(self.entry_p3_list)

class KWykluczen(ctk.CTkFrame):
    def __init__(self, master, db_name, id_n):
        super().__init__(master)
        self.db_name = db_name
        self.id_n = id_n
        self.entry_godziny = []
        self.entry_dnia = []
        self.wykluczenia_widgets = []
        self.entry_dnia_cal = []
        self.wykluczenia_dnia_widgets = []

        ctk.CTkLabel(self, text=f"Nauczyciel: {liczby_danych_uniwersalne(f"select nazwisko from nauczyciele where id_nauczyciela = {self.id_n}", self.db_name)}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        self.scrollbar_left = CTkScrollableFrame(self)
        self.scrollbar_left.pack(fill="both", expand=True, side="left")

        self.scrollbar_right = CTkScrollableFrame(self)
        self.scrollbar_right.pack(fill="both", expand=True, side="right")

        CTkButton(self.scrollbar_left, text="dodaj wykluczenie godziny", command=lambda: self.dodaj_wykluczenie()).pack(pady=10)
        CTkButton(self.scrollbar_right, text="dodaj wykluczenie dnia", command=lambda: self.dodaj_wykluczenie_dnia()).pack(pady=10)

        wykluczenie = pobierz_dane_uniwersalnie(f"select id_klikniecia, godzina, dzien from wykluczenia where id_nauczyciela = {self.id_n}", self.db_name)
        wykluczenie_dnia = pobierz_dane_uniwersalnie(f"select id_klikniecia_dnia, dzien_caly from wykluczenia_dnia where id_nauczyciela = {self.id_n}", self.db_name)
        self.wg_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]
        self.wd_list = ["1", "2", "3", "4", "5"]

        for index, (id_klikniecia, godzina, dzien) in enumerate(wykluczenie, start=1):
            row_frame = ctk.CTkFrame(self.scrollbar_left)
            row_frame.pack(fill="x", pady=2)

            label = CTkLabel(row_frame, text=f"wykluczenie nr: {index}   ")
            label.pack(pady=10, side="left")

            podstawowa_wartosc_g = tk.StringVar(value=liczby_danych_uniwersalne(f"select godzina from wykluczenia where id_klikniecia = {id_klikniecia} and id_nauczyciela = {self.id_n}", self.db_name))
            podstawowa_wartosc_d = tk.StringVar(value=liczby_danych_uniwersalne(f"select dzien from wykluczenia where id_klikniecia = {id_klikniecia} and id_nauczyciela = {self.id_n}", self.db_name))

            lista_wg = ctk.CTkComboBox(row_frame, values=self.wg_list, variable=podstawowa_wartosc_g, command=lambda _, klikniecie_id=id_klikniecia: self.aktualizuj_wykluczenia(klikniecie_id))
            lista_wg.pack(pady=10, padx=5, side="left")
            lista_wd = ctk.CTkComboBox(row_frame, values=self.wd_list, variable=podstawowa_wartosc_d, command=lambda _, klikniecie_id=id_klikniecia: self.aktualizuj_wykluczenia(klikniecie_id))
            lista_wd.pack(pady=10, padx=5, side="left")

            btn_usun = ctk.CTkButton(row_frame, text="x", font=("Arial", 12, "bold"), width=10, command=lambda f=row_frame, id1=id_klikniecia: self.usun_wykluczenie(id1, f))
            btn_usun.pack(side="right", padx=5)

            self.entry_godziny.append({"id": id_klikniecia, "entry": lista_wg})
            self.entry_dnia.append({"id": id_klikniecia, "entry": lista_wd})
            self.wykluczenia_widgets.append({"frame": row_frame, "id": id_klikniecia, "label": label})

        for indexv2, (id_klik, dzien_caly) in enumerate(wykluczenie_dnia, start=1):
            row_frame = ctk.CTkFrame(self.scrollbar_right)
            row_frame.pack(fill="x", pady=2)

            label = CTkLabel(row_frame, text=f"wykluczenie dnia nr: {indexv2}   ")
            label.pack(pady=10, side="left")

            podstawowa_wartosc_dnia = tk.StringVar(value=liczby_danych_uniwersalne(f"select dzien_caly from wykluczenia_dnia where id_klikniecia_dnia = {id_klik} and id_nauczyciela = {self.id_n}", self.db_name))

            lista_wdc = ctk.CTkComboBox(row_frame, values=self.wd_list, variable=podstawowa_wartosc_dnia, command=lambda _, klikniecie_id=id_klik: self.aktualizuj_wykluczenia_dnia(klikniecie_id))
            lista_wdc.pack(pady=10, padx=5, side="left")

            btn_usun = ctk.CTkButton(row_frame, text="x", font=("Arial", 12, "bold"), width=10, command=lambda f=row_frame, id1=id_klik: self.usun_wykluczenie_dnia(id1, f))
            btn_usun.pack(side="right", padx=5)

            self.entry_dnia_cal.append({"id": id_klik, "entry": lista_wdc})
            self.wykluczenia_dnia_widgets.append({"frame": row_frame, "id": id_klik, "label": label})

    def dodaj_wykluczenie(self):
        nowe_id_klikniecia = liczby_danych_uniwersalne(f"SELECT COALESCE(MAX(id_klikniecia), 0) FROM wykluczenia WHERE id_nauczyciela = {self.id_n}", self.db_name) + 1

        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO wykluczenia(id_klikniecia, id_nauczyciela, godzina, dzien) VALUES(?, ?, ?, ?)",(nowe_id_klikniecia, self.id_n, 1, 1))
            conn.commit()
            print("Dane dodane pomyślnie.")
        except sqlite3.Error as e:
            print("Błąd podczas dodawania danych:", e)
            return
        finally:
            conn.close()

        row_frame = ctk.CTkFrame(self.scrollbar_left)
        row_frame.pack(fill="x", pady=2)

        label = CTkLabel(row_frame, text=f"wykluczenie nr: {len(self.wykluczenia_widgets) + 1}")
        label.pack(pady=10, side="left")

        lista_wg = ctk.CTkComboBox(row_frame, values=self.wg_list, command=lambda _, lekcja_id=nowe_id_klikniecia: self.aktualizuj_wykluczenia(lekcja_id))
        lista_wg.pack(pady=10, padx=5, side="left")
        lista_wd = ctk.CTkComboBox(row_frame, values=self.wd_list, command=lambda _, lekcja_id=nowe_id_klikniecia: self.aktualizuj_wykluczenia(lekcja_id))
        lista_wd.pack(pady=10, padx=5, side="left")

        btn_usun = ctk.CTkButton(row_frame, text="x", font=("Arial", 12, "bold"), width=10, command=lambda f=row_frame, id1=nowe_id_klikniecia: self.usun_wykluczenie(id1, f))
        btn_usun.pack(side="right", padx=5)

        self.entry_godziny.append({"id": nowe_id_klikniecia, "entry": lista_wg})
        self.entry_dnia.append({"id": nowe_id_klikniecia, "entry": lista_wd})
        self.wykluczenia_widgets.append({"frame": row_frame, "id": nowe_id_klikniecia, "label": label})
        self.odswiez_numery()

    def dodaj_wykluczenie_dnia(self):
        nowe_id_klikniecia = liczby_danych_uniwersalne(f"SELECT COALESCE(MAX(id_klikniecia_dnia), 0) FROM wykluczenia_dnia WHERE id_nauczyciela = {self.id_n}", self.db_name) + 1

        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO wykluczenia_dnia(id_klikniecia_dnia, id_nauczyciela, dzien_caly) VALUES(?, ?, ?)",(nowe_id_klikniecia, self.id_n, 1))
            conn.commit()
            print("Dane dodane pomyślnie.")
        except sqlite3.Error as e:
            print("Błąd podczas dodawania danych:", e)
            return
        finally:
            conn.close()

        row_frame = ctk.CTkFrame(self.scrollbar_right)
        row_frame.pack(fill="x", pady=2)

        label = CTkLabel(row_frame, text=f"wykluczenie dnia nr: {len(self.wykluczenia_dnia_widgets) + 1}")
        label.pack(pady=10, side="left")

        lista_wdc = ctk.CTkComboBox(row_frame, values=self.wd_list, command=lambda _, klikniecie_id=nowe_id_klikniecia: self.aktualizuj_wykluczenia_dnia(klikniecie_id))
        lista_wdc.pack(pady=10, padx=5, side="left")

        btn_usun = ctk.CTkButton(row_frame, text="x", font=("Arial", 12, "bold"), width=10, command=lambda f=row_frame, id1=nowe_id_klikniecia: self.usun_wykluczenie_dnia(id1, f))
        btn_usun.pack(side="right", padx=5)

        self.entry_dnia_cal.append({"id": nowe_id_klikniecia, "entry": lista_wdc})
        self.wykluczenia_dnia_widgets.append({"frame": row_frame, "id": nowe_id_klikniecia, "label": label})
        self.odswiez_numery_dnia()

    def odswiez_numery(self):
        for i, nauczyciel in enumerate(self.wykluczenia_widgets, start=1):
            nauczyciel["label"].configure(text=f"wykluczenie nr: {i}    ")
            print(self.wykluczenia_widgets)
            print(self.entry_godziny)
            print(self.entry_dnia)

    def odswiez_numery_dnia(self):
        for i, nauczyciel in enumerate(self.wykluczenia_dnia_widgets, start=1):
            nauczyciel["label"].configure(text=f"wykluczenie dnia nr: {i}    ")
            print(self.wykluczenia_dnia_widgets)
            print(self.entry_dnia_cal)

    def aktualizuj_wykluczenia(self, id_klikniecia):
        print(f"wykluczenie ID={id_klikniecia} edytowany")
        entry_g = next((e["entry"] for e in self.entry_godziny if e["id"] == id_klikniecia), None)
        entry_d = next((e["entry"] for e in self.entry_dnia if e["id"] == id_klikniecia), None)
        if entry_g is None and entry_d is None:
            print(f"Nie znaleziono entry dla lekcji ID={id_klikniecia}")
            return

        godzina = entry_g.get()
        godzina_convert = int(godzina)
        dzien = entry_d.get()
        dzien_convert = int(dzien)
        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE wykluczenia SET godzina = ?, dzien = ? WHERE id_nauczyciela = ? AND id_klikniecia = ?",(godzina_convert, dzien_convert, self.id_n, id_klikniecia))
            conn.commit()
            print("Dane edytowane pomyślnie.")
        except sqlite3.Error as e:
            print("Błąd podczas edycji danych:", e)
        finally:
            conn.close()

    def aktualizuj_wykluczenia_dnia(self, id_klikniecia):
        print(f"wykluczenie dnia ID={id_klikniecia} edytowany")
        entry_dc = next((e["entry"] for e in self.entry_dnia_cal if e["id"] == id_klikniecia), None)
        if entry_dc is None:
            print(f"Nie znaleziono entry dla lekcji ID={id_klikniecia}")
            return

        dzien = entry_dc.get()
        dzien_convert = int(dzien)
        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE wykluczenia_dnia SET dzien_caly = ? WHERE id_nauczyciela = ? AND id_klikniecia_dnia = ?",(dzien_convert, self.id_n, id_klikniecia))
            conn.commit()
            print("Dane edytowane pomyślnie.")
        except sqlite3.Error as e:
            print("Błąd podczas edycji danych:", e)
        finally:
            conn.close()

    def usun_wykluczenie(self, id_klikniecia, frame):
        print(f"Usuwanie wykluczenia ID={self.id_n}")
        frame.destroy()

        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM wykluczenia WHERE Id_nauczyciela = ? and id_klikniecia = ?", (self.id_n, id_klikniecia))
            conn.commit()
        except sqlite3.Error as e:
            print("Błąd podczas usuwania:", e)
        finally:
            conn.close()

        self.wykluczenia_widgets = [w for w in self.wykluczenia_widgets if w["id"] != id_klikniecia]
        self.entry_godziny = [e for e in self.entry_godziny if e["id"] != id_klikniecia]
        self.entry_dnia = [e for e in self.entry_dnia if e["id"] != id_klikniecia]
        self.odswiez_numery()
        print(self.wykluczenia_widgets)
        print(self.entry_godziny)
        print(self.entry_dnia)

    def usun_wykluczenie_dnia(self, id_klikniecia, frame):
        print(f"Usuwanie wykluczenia dnia ID={self.id_n}")
        frame.destroy()

        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM wykluczenia_dnia WHERE Id_nauczyciela = ? and id_klikniecia_dnia = ?", (self.id_n, id_klikniecia))
            conn.commit()
        except sqlite3.Error as e:
            print("Błąd podczas usuwania:", e)
        finally:
            conn.close()

        self.wykluczenia_dnia_widgets = [w for w in self.wykluczenia_dnia_widgets if w["id"] != id_klikniecia]
        self.entry_dnia_cal = [e for e in self.entry_dnia_cal if e["id"] != id_klikniecia]
        self.odswiez_numery_dnia()
        print(self.wykluczenia_dnia_widgets)
        print(self.entry_dnia_cal)

class Przypisanie(ctk.CTkFrame):
    def __init__(self, master, sidebar, db_name):
        super().__init__(master)
        self.db_name = db_name
        self.sidebar = sidebar
        self.main = master

        for widget in self.sidebar.winfo_children():
            widget.destroy()

        self.scrollbar_side = CTkScrollableFrame(self.sidebar)
        self.scrollbar_side.pack(fill="both", expand=True)

        ctk.CTkLabel(self.scrollbar_side, text=f"Baza: {db_name}", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=(20, 10))

        id_na = pobierz_dane_uniwersalnie("select id_nauczyciela, nazwisko from nauczyciele", self.db_name)
        print(id_na)
        row = 1
        for index, (id_n, nazwisko) in enumerate(id_na, start=1):
            ctk.CTkButton(self.scrollbar_side, text=f"{nazwisko}", command=lambda id1 = id_n: self.przypisanie_nauczyciela(id1)).grid(row=row, column=0, padx=10, pady=10, sticky="ew")
            row += 1
        ctk.CTkButton(self.scrollbar_side, text="← Wróć do baz", command=self.back_to_menu, fg_color="purple").grid(row=row, column=0, padx=10, pady=10, sticky="ew")

    def back_to_menu(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        app.enter_database_mode(self.db_name)

    def clear_main_view(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def przypisanie_nauczyciela(self, id_naucz):
        self.clear_main_view()
        self.current_view = Konstruktor(self.main, self.db_name, id_naucz)
        self.current_view.pack(fill="both", expand=True)

class Konstruktor(ctk.CTkFrame):
    def __init__(self, master, db_name, id_n):
        super().__init__(master)
        self.db_name = db_name
        self.id_n = id_n
        self.przypisania_widgets = []
        self.entry_przypisanie_list = []

        ctk.CTkLabel(self, text=f"Nauczyciel: {liczby_danych_uniwersalne(f"select nazwisko from nauczyciele where id_nauczyciela = {self.id_n}", self.db_name)}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        CTkButton(self, text="dodaj przypisanie", command=lambda: self.dodaj_przypisanie()).pack(pady=10)

        self.scrollbar = CTkScrollableFrame(self)
        self.scrollbar.pack(fill="both", expand=True)

        lista_przedmiotow = pobierz_dane_uniwersalnie("select nazwa_p from przedmioty", self.db_name)
        self.lista_przedmiotow_reforme = [row[0] for row in lista_przedmiotow]

        przypisanie = pobierz_dane_uniwersalnie(f"select id_lekcji, id_przedmiotu from przypisanie where id_nauczyciela = {self.id_n}", self.db_name)

        for index, (id_lekcji, id_p) in enumerate(przypisanie, start=1):
            row_frame = ctk.CTkFrame(self.scrollbar)
            row_frame.pack(fill="x", pady=2)

            label = CTkLabel(row_frame, text=f"przypisanie nr: {index}   ")
            label.pack(pady=10, side="left")

            podstawowa_wartosc = tk.StringVar(value=liczby_danych_uniwersalne(f"select nazwa_p from przedmioty where id_przedmiotu = (select id_przedmiotu from przypisanie where id_nauczyciela = {self.id_n} and id_lekcji = {id_lekcji})", self.db_name))

            lista_p = ctk.CTkOptionMenu(row_frame, values=self.lista_przedmiotow_reforme, variable=podstawowa_wartosc, command=lambda _, lekcja_id=id_lekcji: self.aktualizuj_przypisanie(lekcja_id))
            lista_p.pack(pady=10, side="left")

            btn_usun = ctk.CTkButton(row_frame, text="x", font=("Arial", 12, "bold"), width=10, command=lambda f=row_frame, id1=id_lekcji: self.usun_przypisanie(id1, f))
            btn_usun.pack(side="right", padx=5)

            self.entry_przypisanie_list.append({"id": id_lekcji, "entry": lista_p})
            self.przypisania_widgets.append({"frame": row_frame, "id": id_lekcji, "label": label})

    def dodaj_przypisanie(self):
        nowe_id_lekcji = liczby_danych_uniwersalne(f"SELECT COALESCE(MAX(id_lekcji), 0) FROM przypisanie WHERE id_nauczyciela = {self.id_n}", self.db_name) + 1

        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO przypisanie(id_lekcji, id_nauczyciela, id_przedmiotu) VALUES(?, ?, ?)",(nowe_id_lekcji, self.id_n, 1))
            conn.commit()
            print("Dane dodane pomyślnie.")
        except sqlite3.Error as e:
            print("Błąd podczas dodawania danych:", e)
            return
        finally:
            conn.close()

        row_frame = ctk.CTkFrame(self.scrollbar)
        row_frame.pack(fill="x", pady=2)

        label = CTkLabel(row_frame, text=f"przypisanie nr: {len(self.przypisania_widgets) + 1}")
        label.pack(pady=10, side="left")

        lista_p = ctk.CTkOptionMenu(row_frame, values=self.lista_przedmiotow_reforme, command=lambda _, lekcja_id=nowe_id_lekcji: self.aktualizuj_przypisanie(lekcja_id))
        lista_p.pack(pady=10, side="left")

        btn_usun = ctk.CTkButton(row_frame, text="x", font=("Arial", 12, "bold"), width=10, command=lambda f=row_frame, id1=nowe_id_lekcji: self.usun_przypisanie(id1, f))
        btn_usun.pack(side="right", padx=5)

        self.entry_przypisanie_list.append({"id": nowe_id_lekcji, "entry": lista_p})
        self.przypisania_widgets.append({"frame": row_frame, "id": nowe_id_lekcji, "label": label})
        self.odswiez_numery()

    def odswiez_numery(self):
        for i, nauczyciel in enumerate(self.przypisania_widgets, start=1):
            nauczyciel["label"].configure(text=f"przypisanie nr: {i}    ")
            print(self.przypisania_widgets)
            print(self.entry_przypisanie_list)

    def aktualizuj_przypisanie(self, id_lekcji):
        print(f"przypisanie ID={id_lekcji} edytowany")
        entry = next((e["entry"] for e in self.entry_przypisanie_list if e["id"] == id_lekcji), None)
        if entry is None:
            print(f"Nie znaleziono entry dla lekcji ID={id_lekcji}")
            return

        nazwa = entry.get()
        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id_przedmiotu FROM przedmioty WHERE nazwa_p = ?", (nazwa,))
            wynik = cursor.fetchone()
            if wynik:
                id_przedmiotu = wynik[0]
                cursor.execute("UPDATE przypisanie SET id_przedmiotu = ? WHERE id_nauczyciela = ? AND id_lekcji = ?",(id_przedmiotu, self.id_n, id_lekcji))
                conn.commit()
                print("Dane edytowane pomyślnie.")
            else:
                print(f"Nie znaleziono przedmiotu o nazwie: {nazwa}")
        except sqlite3.Error as e:
            print("Błąd podczas edycji danych:", e)
        finally:
            conn.close()

    def usun_przypisanie(self, id_lekcji, frame):
        print(f"Usuwanie przedmiotu ID={self.id_n}")
        frame.destroy()

        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM przypisanie WHERE Id_nauczyciela = ? and id_lekcji = ?", (self.id_n, id_lekcji))
            conn.commit()
        except sqlite3.Error as e:
            print("Błąd podczas usuwania:", e)
        finally:
            conn.close()

        self.przypisania_widgets = [w for w in self.przypisania_widgets if w["id"] != id_lekcji]
        self.entry_przypisanie_list = [e for e in self.entry_przypisanie_list if e["id"] != id_lekcji]
        self.odswiez_numery()
        print(self.przypisania_widgets)
        print(self.entry_przypisanie_list)

class Przedmioty(ctk.CTkFrame):
    def __init__(self, master, db_name):
        super().__init__(master)
        self.db_name = db_name
        self.przedmioty_widgets = []
        self.entry_przedmiot_list = []

        CTkButton(self, text="dodaj przedmiot", command=lambda: self.dodaj_przedmiot()).pack(pady=10)

        self.scrollbar = CTkScrollableFrame(self)
        self.scrollbar.pack(fill="both", expand=True)

        przedmioty = pobierz_dane_uniwersalnie("SELECT id_przedmiotu, nazwa_p FROM przedmioty", self.db_name)

        for index, (id_n, nazwa) in enumerate(przedmioty, start=1):
            row_frame = ctk.CTkFrame(self.scrollbar)
            row_frame.pack(fill="x", pady=2)

            label = CTkLabel(row_frame, text=f"przedmiot nr: {index}   ")
            label.pack(pady=10, side="left")

            entry_przedmiotu = ctk.CTkEntry(row_frame)
            entry_przedmiotu.insert(0, nazwa)
            entry_przedmiotu.pack(side="left")

            self.entry_przedmiot_list.append({"id": id_n, "entry": entry_przedmiotu})

            btn_edytuj = ctk.CTkButton(row_frame, text="?", font=("Arial", 12, "bold"), width=10, command=lambda id1=id_n: self.aktualizuj_przedmiot(id1))
            btn_edytuj.pack(side="right", padx=5)

            btn_usun = ctk.CTkButton(row_frame, text="x", font=("Arial", 12, "bold"), width=10, command=lambda f=row_frame, id1=id_n: self.usun_przedmiot(id1, f))
            btn_usun.pack(side="right", padx=5)

            self.przedmioty_widgets.append({"frame": row_frame, "id": id_n, "label": label})

    def dodaj_przedmiot(self):
        row_frame = ctk.CTkFrame(self.scrollbar)
        row_frame.pack(fill="x", pady=2)

        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO przedmioty(nazwa_p) VALUES(?)", ("edycja",))
            id_n = cursor.lastrowid
            print(id_n)
            conn.commit()
            print("Dane dodane pomyślnie.")
        except sqlite3.Error as e:
            print("Błąd podczas dodawania danych:", e)
            return
        finally:
            conn.close()

        label = CTkLabel(row_frame, text=f"przedmiot nr: {len(self.przedmioty_widgets)+1}")
        label.pack(pady=10, side="left")

        entry = ctk.CTkEntry(row_frame)
        entry.insert(0, "edycja")
        entry.pack(side="left")
        self.entry_przedmiot_list.append({"id": id_n, "entry": entry})

        btn_edytuj = ctk.CTkButton(row_frame, text="?", font=("Arial", 12, "bold"), width=10, command=lambda id1=id_n: self.aktualizuj_przedmiot(id1))
        btn_edytuj.pack(side="right", padx=5)

        btn_usun = ctk.CTkButton(row_frame, text="x", font=("Arial", 12, "bold"), width=10, command=lambda f=row_frame, id1=id_n: self.usun_przedmiot(id1, f))
        btn_usun.pack(side="right", padx=5)

        self.przedmioty_widgets.append({"frame": row_frame, "id": id_n, "label": label})
        self.odswiez_numery()
        print(self.entry_przedmiot_list)
        print(self.przedmioty_widgets)

    def aktualizuj_przedmiot(self, id_n):
        print(f"przedmiot ID={id_n} edytowany")
        entry = next((e["entry"] for e in self.entry_przedmiot_list if e["id"] == id_n), None)
        if entry is None:
            print(f"Nie znaleziono entry dla przedmiotu ID={id_n}")
            return
        nazwa = entry.get()

        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE przedmioty SET nazwa_p = ? WHERE id_przedmiotu = ?", (nazwa, id_n))
            conn.commit()
            print("Dane edytowane pomyślnie.")
        except sqlite3.Error as e:
            print("Błąd podczas edycji danych:", e)
        finally:
            conn.close()

    def usun_przedmiot(self, id_n, frame):
        print(f"Usuwanie przedmiotu ID={id_n}")
        frame.destroy()
        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM przedmioty WHERE Id_przedmiotu = ?", (id_n,))
            cursor.execute("DELETE FROM przypisanie WHERE Id_przedmiotu = ?", (id_n,))
            cursor.execute("DELETE FROM dzielenia WHERE Id_przedmiotu = ?", (id_n,))
            conn.commit()
        except sqlite3.Error as e:
            print("Błąd podczas usuwania:", e)
        finally:
            conn.close()

        self.przedmioty_widgets = [w for w in self.przedmioty_widgets if w["id"] != id_n]
        self.entry_przedmiot_list = [e for e in self.entry_przedmiot_list if e["id"] != id_n]
        self.odswiez_numery()
        print(self.przedmioty_widgets)
        print(self.entry_przedmiot_list)

    def odswiez_numery(self):
        for i, nauczyciel in enumerate(self.przedmioty_widgets, start=1):
            nauczyciel["label"].configure(text=f"przedmiot nr: {i}    ")
            print(self.przedmioty_widgets)
            print(self.entry_przedmiot_list)

class Klasy(ctk.CTkFrame):
    def __init__(self, master, db_name):
        super().__init__(master)
        self.db_name = db_name
        self.klasy_widgets = []
        self.entry_klas_list = []

        CTkButton(self, text="dodaj klasy", command=lambda: self.dodaj_klasy()).pack(pady=10)

        self.scrollbar = CTkScrollableFrame(self)
        self.scrollbar.pack(fill="both", expand=True)

        klasy = pobierz_dane_uniwersalnie("SELECT id_klasy, nazwa FROM klasy", self.db_name)

        for index, (id_n, nazwa) in enumerate(klasy, start=1):
            row_frame = ctk.CTkFrame(self.scrollbar)
            row_frame.pack(fill="x", pady=2)

            label = CTkLabel(row_frame, text=f"klasa nr: {index}   ")
            label.pack(pady=10, side="left")

            entry_klasy = ctk.CTkEntry(row_frame)
            entry_klasy.insert(0, nazwa)
            entry_klasy.pack(side="left")

            self.entry_klas_list.append({"id": id_n, "entry": entry_klasy})

            btn_edytuj = ctk.CTkButton(row_frame, text="?", font=("Arial", 12, "bold"), width=10, command=lambda id1=id_n: self.aktualizuj_klasy(id1))
            btn_edytuj.pack(side="right", padx=5)

            btn_usun = ctk.CTkButton(row_frame, text="x", font=("Arial", 12, "bold"), width=10, command=lambda f=row_frame, id1=id_n: self.usun_klasy(id1, f))
            btn_usun.pack(side="right", padx=5)

            self.klasy_widgets.append({"frame": row_frame, "id": id_n, "label": label})

    def dodaj_klasy(self):
        row_frame = ctk.CTkFrame(self.scrollbar)
        row_frame.pack(fill="x", pady=2)

        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO klasy(nazwa) VALUES(?)", ("edycja",))
            id_n = cursor.lastrowid
            print(id_n)
            conn.commit()
            print("Dane dodane pomyślnie.")
        except sqlite3.Error as e:
            print("Błąd podczas dodawania danych:", e)
            return
        finally:
            conn.close()

        label = CTkLabel(row_frame, text=f"klasa nr: {len(self.klasy_widgets)+1}")
        label.pack(pady=10, side="left")

        entry = ctk.CTkEntry(row_frame)
        entry.insert(0, "edycja")
        entry.pack(side="left")
        self.entry_klas_list.append({"id": id_n, "entry": entry})

        btn_edytuj = ctk.CTkButton(row_frame, text="?", font=("Arial", 12, "bold"), width=10, command=lambda id1=id_n: self.aktualizuj_klasy(id1))
        btn_edytuj.pack(side="right", padx=5)

        btn_usun = ctk.CTkButton(row_frame, text="x", font=("Arial", 12, "bold"), width=10, command=lambda f=row_frame, id1=id_n: self.usun_klasy(id1, f))
        btn_usun.pack(side="right", padx=5)

        self.klasy_widgets.append({"frame": row_frame, "id": id_n, "label": label})
        self.odswiez_numery()
        print(self.entry_klas_list)
        print(self.klasy_widgets)

    def aktualizuj_klasy(self, id_n):
        print(f"Nauczyciel ID={id_n} edytowany")
        entry = next((e["entry"] for e in self.entry_klas_list if e["id"] == id_n), None)
        if entry is None:
            print(f"Nie znaleziono entry dla klasy ID={id_n}")
            return
        nazwa = entry.get()

        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE klasy SET nazwa = ? WHERE id_klasy = ?", (nazwa, id_n))
            conn.commit()
            print("Dane edytowane pomyślnie.")
        except sqlite3.Error as e:
            print("Błąd podczas edycji danych:", e)
        finally:
            conn.close()

    def usun_klasy(self, id_n, frame):
        print(f"Usuwanie klasy ID={id_n}")
        frame.destroy()

        conn = sqlite3.connect(f"{self.db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM klasy WHERE Id_klasy = ?", (id_n,))
            cursor.execute("DELETE FROM dzielenia WHERE Id_klasy = ?", (id_n,))
            conn.commit()
        except sqlite3.Error as e:
            print("Błąd podczas usuwania:", e)
        finally:
            conn.close()

        self.klasy_widgets = [w for w in self.klasy_widgets if w["id"] != id_n]
        self.entry_klas_list = [e for e in self.entry_klas_list if e["id"] != id_n]
        self.odswiez_numery()
        print(self.klasy_widgets)
        print(self.entry_klas_list)

    def odswiez_numery(self):
        for i, nauczyciel in enumerate(self.klasy_widgets, start=1):
            nauczyciel["label"].configure(text=f"klasa nr: {i}    ")
            print(self.klasy_widgets)
            print(self.entry_klas_list)

class Nauczyciele(ctk.CTkFrame):
    def __init__(self, master, db_name):
        super().__init__(master)
        self.db_name = db_name
        self.nauczyciele_widgets = []
        self.entry_nauczycieli_list = []

        CTkButton(self, text="dodaj nauczyciela", command=lambda: self.dodaj_naucz(db_name)).pack(pady=10)

        self.scrollbar = CTkScrollableFrame(self)
        self.scrollbar.pack(fill="both", expand=True)

        nauczyciele = pobierz_dane_uniwersalnie("SELECT id_nauczyciela, nazwisko FROM nauczyciele", self.db_name)

        for index, (id_n, nazwisko) in enumerate(nauczyciele, start=1):
            row_frame = ctk.CTkFrame(self.scrollbar)
            row_frame.pack(fill="x", pady=2)

            label = CTkLabel(row_frame, text=f"nauczyciel nr: {index}   ")
            label.pack(pady=10, side="left")

            entry_nauczyciela = ctk.CTkEntry(row_frame)
            entry_nauczyciela.insert(0, nazwisko)
            entry_nauczyciela.pack(side="left")

            self.entry_nauczycieli_list.append({"id": id_n, "entry": entry_nauczyciela})

            btn_edytuj = ctk.CTkButton(row_frame, text="?", font=("Arial", 12, "bold"), width=10, command=lambda id1=id_n: self.aktualizuj_naucz(id1, db_name))
            btn_edytuj.pack(side="right", padx=5)

            btn_usun = ctk.CTkButton(row_frame, text="x", font=("Arial", 12, "bold"), width=10, command=lambda f=row_frame, id1=id_n: self.usun_naucz(id1, f, db_name))
            btn_usun.pack(side="right", padx=5)

            self.nauczyciele_widgets.append({"frame": row_frame, "id": id_n, "label": label})

    def dodaj_naucz(self, db_name):
        row_frame = ctk.CTkFrame(self.scrollbar)
        row_frame.pack(fill="x", pady=2)

        conn = sqlite3.connect(f"{db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO nauczyciele(nazwisko) VALUES(?)", ("edycja",))
            id_n = cursor.lastrowid
            print(id_n)

            cursor.execute("INSERT INTO klasy_nauczyciele(id_nauczyciela, czy_loczony_naucz) VALUES(?, ?)", (id_n, 0))

            for hd in range(liczby_danych_uniwersalne("SELECT COUNT(nazwa) FROM klasy", db_name)):
                cursor.execute("INSERT INTO godziny(id_nauczyciela, id_klasy, godzina) VALUES (?, ?, ?)", (id_n, hd + 1, 0))
                cursor.execute("INSERT INTO loczenia_grup(id_klasy, id_nauczyciela, czy_loczona, ilosc_godzin) VALUES (?, ?, 0, 0)", (hd + 1, id_n))
                cursor.execute("INSERT INTO klasy_nauczyciele_nnk(id_klasy, id_nauczyciela, czy_loczony_klasa) VALUES (?, ?, 0)", (hd + 1, id_n))

            conn.commit()
            print("Dane dodane pomyślnie.")
        except sqlite3.Error as e:
            print("Błąd podczas dodawania danych:", e)
            return
        finally:
            conn.close()

        label = CTkLabel(row_frame, text=f"nauczyciel nr: {len(self.nauczyciele_widgets)+1}")
        label.pack(pady=10, side="left")

        entry = ctk.CTkEntry(row_frame)
        entry.insert(0, "edycja")
        entry.pack(side="left")
        self.entry_nauczycieli_list.append({"id": id_n, "entry": entry})

        btn_edytuj = ctk.CTkButton(row_frame, text="?", font=("Arial", 12, "bold"), width=10, command=lambda id1=id_n: self.aktualizuj_naucz(id1, db_name))
        btn_edytuj.pack(side="right", padx=5)

        btn_usun = ctk.CTkButton(row_frame, text="x", font=("Arial", 12, "bold"), width=10, command=lambda f=row_frame, id1=id_n: self.usun_naucz(id1, f, db_name))
        btn_usun.pack(side="right", padx=5)

        self.nauczyciele_widgets.append({"frame": row_frame, "id": id_n, "label": label})
        self.odswiez_numery()
        print(self.entry_nauczycieli_list)
        print(self.nauczyciele_widgets)

    def aktualizuj_naucz(self, id_n, db_name):
        print(f"Nauczyciel ID={id_n} edytowany")
        entry = next((e["entry"] for e in self.entry_nauczycieli_list if e["id"] == id_n), None)
        if entry is None:
            print(f"Nie znaleziono entry dla nauczyciela ID={id_n}")
            return
        nazwisko = entry.get()

        conn = sqlite3.connect(f"{db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE nauczyciele SET nazwisko = ? WHERE id_nauczyciela = ?", (nazwisko, id_n))
            conn.commit()
            print("Dane edytowane pomyślnie.")
        except sqlite3.Error as e:
            print("Błąd podczas edycji danych:", e)
        finally:
            conn.close()

    def usun_naucz(self, id_n, frame, db_name):
        print(f"Usuwanie nauczyciela ID={id_n}")
        frame.destroy()

        conn = sqlite3.connect(f"{db_name}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM nauczyciele WHERE id_nauczyciela = ?", (id_n,))
            cursor.execute("DELETE FROM przypisanie WHERE id_nauczyciela = ?", (id_n,))
            cursor.execute("DELETE FROM dzielenia WHERE id_nauczyciela = ?", (id_n,))
            conn.commit()
        except sqlite3.Error as e:
            print("Błąd podczas usuwania:", e)
        finally:
            conn.close()

        self.nauczyciele_widgets = [w for w in self.nauczyciele_widgets if w["id"] != id_n]
        self.entry_nauczycieli_list = [e for e in self.entry_nauczycieli_list if e["id"] != id_n]
        self.odswiez_numery()
        print(self.nauczyciele_widgets)
        print(self.entry_nauczycieli_list)

    def odswiez_numery(self):
        for i, nauczyciel in enumerate(self.nauczyciele_widgets, start=1):
            nauczyciel["label"].configure(text=f"nauczyciel nr: {i}")
            print(self.nauczyciele_widgets)
            print(self.entry_nauczycieli_list)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()

