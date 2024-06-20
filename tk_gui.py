from tkinter import *

import requests
import tkintermapview
from bs4 import BeautifulSoup

from tkinter import messagebox
import logging

logging.basicConfig(filename='program.log', format='%(message)s')

# Dane logowania
uzytkownicy = {
    'user': 'geoinfa rządzi',
}


# Funkcja logowania
def zaloguj():
    username = entry_username.get()
    password = entry_password.get()

    if username in uzytkownicy and uzytkownicy[username] == password:
        messagebox.showinfo("Sukces", "Zalogowano pomyślnie!")
        okno_logowania.destroy()
    else:
        messagebox.showerror("Błąd logowania", "Niepoprawny użytkownik lub hasło.")
        entry_username.delete(0, END)
        entry_password.delete(0, END)


# Tworzenie okna logowania
okno_logowania = Tk()
okno_logowania.title("Logowanie")
okno_logowania.geometry("300x150")

Label(okno_logowania, text="Użytkownik:").pack()
entry_username = Entry(okno_logowania)
entry_username.pack()

Label(okno_logowania, text="Hasło:").pack()
entry_password = Entry(okno_logowania, show="*")
entry_password.pack()

Button(okno_logowania, text="Zaloguj", command=zaloguj).pack()

okno_logowania.mainloop()

firmy = []
klienci = []
pracownicy = []


class user:
    def __init__(self, nazwa, lokalizacja, lista_user, widget_maps):
        self.nazwa = nazwa
        self.lokalizacja = lokalizacja
        self.koordynaty = self.pobierz_koordynaty()
        self.marker = widget_maps.set_marker(self.koordynaty[0], self.koordynaty[1], text=self.nazwa)
        lista_user.append(self)

    def pobierz_koordynaty(self):
        url = f'https://pl.wikipedia.org/wiki/{self.lokalizacja}'
        response = requests.get(url)
        response_html = BeautifulSoup(response.text, 'html.parser')
        return [
            float(response_html.select('.latitude')[1].text.replace(",", ".")),
            float(response_html.select('.longitude')[1].text.replace(",", "."))
        ]

    def usun_marker(self):
        self.marker.delete()


class Firma(user):
    def __init__(self, nazwa, lokalizacja, widget_maps):
        super().__init__(nazwa, lokalizacja, firmy, widget_maps)
        self.klienci = []
        self.pracownicy = []


class Klient(user):
    def __init__(self, nazwa, lokalizacja, firma, widget_maps):
        super().__init__(nazwa, lokalizacja, klienci, widget_maps)
        self.firma = firma
        self.firma.klienci.append(self)


class Pracownik(user):
    def __init__(self, nazwa, lokalizacja, firma, widget_maps):
        super().__init__(nazwa, lokalizacja, pracownicy, widget_maps)
        self.firma = firma
        self.firma.pracownicy.append(self)


def pokaz_user(lista_user, lista):
    lista.delete(0, END)
    for user in lista_user:
        lista.insert(END, f'{user.nazwa} - {user.lokalizacja}')


def dodaj_firme():
    nazwa = entry_firma_nazwa.get()
    lokalizacja = entry_firma_lokalizacja.get()
    Firma(nazwa, lokalizacja, widget_mapy)
    pokaz_user(firmy, listbox_firmy)
    entry_firma_nazwa.delete(0, END)
    entry_firma_lokalizacja.delete(0, END)


def dodaj_klienta():
    nazwa = entry_klient_nazwa.get()
    lokalizacja = entry_klient_lokalizacja.get()
    nazwa_firmy = entry_klient_firma.get()
    firma = next((f for f in firmy if f.nazwa == nazwa_firmy), None)
    if firma:
        Klient(nazwa, lokalizacja, firma, widget_mapy)
        pokaz_user(klienci, listbox_klienci)
        entry_klient_nazwa.delete(0, END)
        entry_klient_lokalizacja.delete(0, END)
        entry_klient_firma.delete(0, END)


def dodaj_pracownika():
    nazwa = entry_pracownik_nazwa.get()
    lokalizacja = entry_pracownik_lokalizacja.get()
    nazwa_firmy = entry_pracownik_firma.get()
    firma = next((f for f in firmy if f.nazwa == nazwa_firmy), None)
    if firma:
        Pracownik(nazwa, lokalizacja, firma, widget_mapy)
        pokaz_user(pracownicy, listbox_pracownicy)
        entry_pracownik_nazwa.delete(0, END)
        entry_pracownik_lokalizacja.delete(0, END)
        entry_pracownik_firma.delete(0, END)


def usun_user(lista_user, lista):
    selected_index = lista.curselection()[0]
    entity = lista_user[selected_index]
    entity.usun_marker()
    lista_user.pop(selected_index)
    pokaz_user(lista_user, lista)


def pokaz_szczegoly_firmy():
    selected_index = listbox_firmy.curselection()[0]
    firma = firmy[selected_index]
    pokaz_user(firma.klienci, listbox_klienci)
    pokaz_user(firma.pracownicy, listbox_pracownicy)


def edytuj_firme():
    selected_index = listbox_firmy.curselection()[0]
    firma = firmy[selected_index]
    entry_firma_nazwa.insert(0, firma.nazwa)
    entry_firma_lokalizacja.insert(0, firma.lokalizacja)
    button_dodaj_firme.config(text="Zapisz zmiany", command=lambda: zaktualizuj_firme(selected_index))


def zaktualizuj_firme(index):
    firma = firmy[index]
    firma.nazwa = entry_firma_nazwa.get()
    firma.lokalizacja = entry_firma_lokalizacja.get()
    firma.koordynaty = firma.pobierz_koordynaty()
    firma.usun_marker()
    firma.marker = widget_mapy.set_marker(firma.koordynaty[0], firma.koordynaty[1], text=firma.nazwa)
    pokaz_user(firmy, listbox_firmy)
    button_dodaj_firme.config(text="Dodaj Firmę", command=dodaj_firme)
    entry_firma_nazwa.delete(0, END)
    entry_firma_lokalizacja.delete(0, END)


def edytuj_klienta():
    selected_index = listbox_klienci.curselection()[0]
    klient = klienci[selected_index]
    entry_klient_nazwa.insert(0, klient.nazwa)
    entry_klient_lokalizacja.insert(0, klient.lokalizacja)
    entry_klient_firma.insert(0, klient.firma.nazwa)
    button_dodaj_klienta.config(text="Zapisz zmiany", command=lambda: zaktualizuj_klienta(selected_index))


def zaktualizuj_klienta(index):
    klient = klienci[index]
    klient.nazwa = entry_klient_nazwa.get()
    klient.lokalizacja = entry_klient_lokalizacja.get()
    klient.firma = next((f for f in firmy if f.nazwa == entry_klient_firma.get()), None)
    klient.koordynaty = klient.pobierz_koordynaty()
    klient.usun_marker()
    klient.marker = widget_mapy.set_marker(klient.koordynaty[0], klient.koordynaty[1], text=klient.nazwa)
    pokaz_user(klienci, listbox_klienci)
    button_dodaj_klienta.config(text="Dodaj Klienta", command=dodaj_klienta)
    entry_klient_nazwa.delete(0, END)
    entry_klient_lokalizacja.delete(0, END)
    entry_klient_firma.delete(0, END)


def edytuj_pracownika():
    selected_index = listbox_pracownicy.curselection()[0]
    pracownik = pracownicy[selected_index]
    entry_pracownik_nazwa.insert(0, pracownik.nazwa)
    entry_pracownik_lokalizacja.insert(0, pracownik.lokalizacja)
    entry_pracownik_firma.insert(0, pracownik.firma.nazwa)
    button_dodaj_pracownika.config(text="Zapisz zmiany", command=lambda: zaktualizuj_pracownika(selected_index))


def zaktualizuj_pracownika(index):
    pracownik = pracownicy[index]
    pracownik.nazwa = entry_pracownik_nazwa.get()
    pracownik.lokalizacja = entry_pracownik_lokalizacja.get()
    pracownik.firma = next((f for f in firmy if f.nazwa == entry_pracownik_firma.get()), None)
    pracownik.koordynaty = pracownik.pobierz_koordynaty()
    pracownik.usun_marker()
    pracownik.marker = widget_mapy.set_marker(pracownik.koordynaty[0], pracownik.koordynaty[1], text=pracownik.nazwa)
    pokaz_user(pracownicy, listbox_pracownicy)
    button_dodaj_pracownika.config(text="Dodaj Pracownika", command=dodaj_pracownika)
    entry_pracownik_nazwa.delete(0, END)
    entry_pracownik_lokalizacja.delete(0, END)
    entry_pracownik_firma.delete(0, END)


# Ustawienia GUI
root = Tk()
root.title("Zarządzanie Firmami Edukacyjnymi")
root.geometry("1200x600")

# Ramki
ramka_firmy = Frame(root)
ramka_klienci = Frame(root)
ramka_pracownicy = Frame(root)
ramka_formularz = Frame(root)

ramka_firmy.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)
ramka_klienci.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)
ramka_pracownicy.grid(row=0, column=2, padx=5, pady=5, sticky=N + S + E + W)
ramka_formularz.grid(row=0, column=3, padx=5, pady=5, sticky=N + S + E + W)

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)

# Listboxy i etykiety
Label(ramka_firmy, text="Firmy:").grid(row=0, column=0)
listbox_firmy = Listbox(ramka_firmy, width=30, height=20)
listbox_firmy.grid(row=1, column=0, sticky=N + S + E + W)
Button(ramka_firmy, text="Pokaż Szczegóły", command=pokaz_szczegoly_firmy).grid(row=2, column=0)
Button(ramka_firmy, text="Edytuj Firmę", command=edytuj_firme).grid(row=3, column=0)
Button(ramka_firmy, text="Usuń Firmę", command=lambda: usun_user(firmy, listbox_firmy)).grid(row=4, column=0)

Label(ramka_klienci, text="Klienci:").grid(row=0, column=0)
listbox_klienci = Listbox(ramka_klienci, width=30, height=20)
listbox_klienci.grid(row=1, column=0, sticky=N + S + E + W)
Button(ramka_klienci, text="Edytuj Klienta", command=edytuj_klienta).grid(row=2, column=0)
Button(ramka_klienci, text="Usuń Klienta", command=lambda: usun_user(klienci, listbox_klienci)).grid(row=3, column=0)

Label(ramka_pracownicy, text="Pracownicy:").grid(row=0, column=0)
listbox_pracownicy = Listbox(ramka_pracownicy, width=30, height=20)
listbox_pracownicy.grid(row=1, column=0, sticky=N + S + E + W)
Button(ramka_pracownicy, text="Edytuj Pracownika", command=edytuj_pracownika).grid(row=2, column=0)
Button(ramka_pracownicy, text="Usuń Pracownika", command=lambda: usun_user(pracownicy, listbox_pracownicy)).grid(
    row=3, column=0)

# Formularz do dodawania user
Label(ramka_formularz, text="Dodaj Firmę").grid(row=0, column=0, columnspan=2)
Label(ramka_formularz, text="Nazwa:").grid(row=1, column=0)
entry_firma_nazwa = Entry(ramka_formularz)
entry_firma_nazwa.grid(row=1, column=1)
Label(ramka_formularz, text="Lokalizacja:").grid(row=2, column=0)
entry_firma_lokalizacja = Entry(ramka_formularz)
entry_firma_lokalizacja.grid(row=2, column=1)
button_dodaj_firme = Button(ramka_formularz, text="Dodaj Firmę", command=dodaj_firme)
button_dodaj_firme.grid(row=3, column=0, columnspan=2)

Label(ramka_formularz, text="Dodaj Klienta").grid(row=4, column=0, columnspan=2)
Label(ramka_formularz, text="Nazwa:").grid(row=5, column=0)
entry_klient_nazwa = Entry(ramka_formularz)
entry_klient_nazwa.grid(row=5, column=1)
Label(ramka_formularz, text="Lokalizacja:").grid(row=6, column=0)
entry_klient_lokalizacja = Entry(ramka_formularz)
entry_klient_lokalizacja.grid(row=6, column=1)
Label(ramka_formularz, text="Firma:").grid(row=7, column=0)
entry_klient_firma = Entry(ramka_formularz)
entry_klient_firma.grid(row=7, column=1)
button_dodaj_klienta = Button(ramka_formularz, text="Dodaj Klienta", command=dodaj_klienta)
button_dodaj_klienta.grid(row=8, column=0, columnspan=2)

Label(ramka_formularz, text="Dodaj Pracownika").grid(row=9, column=0, columnspan=2)
Label(ramka_formularz, text="Nazwa:").grid(row=10, column=0)
entry_pracownik_nazwa = Entry(ramka_formularz)
entry_pracownik_nazwa.grid(row=10, column=1)
Label(ramka_formularz, text="Lokalizacja:").grid(row=11, column=0)
entry_pracownik_lokalizacja = Entry(ramka_formularz)
entry_pracownik_lokalizacja.grid(row=11, column=1)
Label(ramka_formularz, text="Firma:").grid(row=12, column=0)
entry_pracownik_firma = Entry(ramka_formularz)
entry_pracownik_firma.grid(row=12, column=1)
button_dodaj_pracownika = Button(ramka_formularz, text="Dodaj Pracownika", command=dodaj_pracownika)
button_dodaj_pracownika.grid(row=13, column=0, columnspan=2)

# Widget mapy
widget_mapy = tkintermapview.TkinterMapView(root, width=900, height=300)
widget_mapy.set_position(52.2, 21.0)
widget_mapy.set_zoom(6)
widget_mapy.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)

root.mainloop()
