import os
from modele import Krasnal, Zloze
from struktury import DrzewoPrzedzialowe
from main import zaladuj_dane


if __name__ == "__main__":
    krasnale, zloza, tabela_odl = zaladuj_dane("dane.json")

    print("=== AKAPIT 4 – DEKAMETROWCY I DRZEWO PRZEDZIAŁOWE ===")
    tablica_granicy = [(k.glosnosc, k.imie) for k in krasnale]
    print(f"Rozstawiono {len(tablica_granicy)} krasnoludków na granicy.")

    drzewo = DrzewoPrzedzialowe(tablica_granicy)

    poczatek = 2
    koniec = 7
    najglosniejszy = drzewo.znajdz_najglosniejszego(poczatek, koniec)
    print(f"\n[ALARM] Atak jabłkami na odcinek od {poczatek} do {koniec} metra!")
    if najglosniejszy[0] != float("-inf"):
        print(f"Najgłośniejszy na tym odcinku to {najglosniejszy[1]} (głośność: {najglosniejszy[0]}).")
        print(f"{najglosniejszy[1]} wydaje rozkaz: strzały na cięciwy – naciągnąć cięciwy – strzał!")