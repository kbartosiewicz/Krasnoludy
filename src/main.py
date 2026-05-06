import json
import os
from modele import Krasnal, Zloze
from przydzial_pracy import MenadzerPrzydzialu
from otoczka import get_convex_hull, calculate_perimeter
from struktury import DrzewoPrzedzialowe 

def zaladuj_dane(plik):
    katalog_skryptu = os.path.dirname(os.path.abspath(__file__))
    pelna_sciezka = os.path.join(katalog_skryptu, plik)
    
    with open(pelna_sciezka, 'r', encoding='utf-8') as f:
        dane = json.load(f)
        
    krasnale = [Krasnal(k['id'], k['imie'], k['umiejetnosci'], k.get('glosnosc', 50)) for k in dane['krasnale']]
    zloza = [Zloze(z['id'], z['nazwa'], z['wydajnosc'], z.get('x', 0.0), z.get('y', 0.0)) for z in dane['zloza']]
    
    tabela_odl = {}
    for o in dane['odleglosci']:
        tabela_odl[(o['krasnal'], o['zloze'])] = o['wartosc']
        
    return krasnale, zloza, tabela_odl

# Użycie:
krasnale, zloza, tabela_odl = zaladuj_dane('dane.json');
menadzer = MenadzerPrzydzialu(krasnale, zloza, tabela_odl)

# Zbudowanie sieci i znalezienie rozwiązania
menadzer.buduj_siec()
przeplyw, koszt = menadzer.oblicz_mcmf()

print("=== RAPORT PRZYDZIAŁU ===")
print(f"Ilość pracujących krasnali (max przepływ): {przeplyw}")
print(f"Łączny pokonany dystans (min koszt): {koszt}")

print("\n=== RAPORT Z TRASY KSIĘCIA ===")
aktywne_zloza = menadzer.daj_aktywne_zloza()
punkty_kopalni = [(z.x, z.y) for z in aktywne_zloza]

if not punkty_kopalni:
    print("Brak pracujących kopalni - książę nie musi dzisiaj patrolować!")
else:
    trasa_ksiecia = get_convex_hull(punkty_kopalni)
    dystans_trasy = calculate_perimeter(trasa_ksiecia)
    
    nazwy_kopalni = [z.nazwa for z in aktywne_zloza]
    print(f"Użytkowane kopalnie: {', '.join(nazwy_kopalni)}")
    print(f"Punkty graniczne patrolu: {trasa_ksiecia}")
    print(f"Najkrótszy obwód do objechania terenu: {dystans_trasy:.2f} m")

# Drzewo Przedziałowe
print("\n=== RAPORT Z OBRONY GRANICY (DEKAMETROWCY) ===")

# Tworzymy tablicę w formacie (glosnosc, imie) na podstawie wczytanych krasnali
tablica_granicy = [(k.glosnosc, k.imie) for k in krasnale]
print(f"Rozstawiono {len(tablica_granicy)} krasnoludków na granicy.")

# Budowa drzewa O(N)
drzewo = DrzewoPrzedzialowe(tablica_granicy)

# Symulacja ataku 1
poczatek = 2
koniec = 7
najglosniejszy = drzewo.znajdz_najglosniejszego(poczatek, koniec)
print(f"\n[ALARM] Atak jabłkami na odcinek od {poczatek} do {koniec} metra!")
if najglosniejszy[0] != float('-inf'):
    print(f"Najgłośniejszy na tym odcinku to {najglosniejszy[1]} (głośność: {najglosniejszy[0]}).")
    print(f"{najglosniejszy[1]} wydaje rozkaz: „strzały na cięciwy – naciągnąć cięciwy – strzał!”")

# Symulacja ataku 2
poczatek2 = 10
koniec2 = 14
najglosniejszy2 = drzewo.znajdz_najglosniejszego(poczatek2, koniec2)
print(f"\n[ALARM] Kolejny atak na odcinek od {poczatek2} do {koniec2} metra!")
if najglosniejszy2[0] != float('-inf'):
    print(f"Najgłośniejszy na tym odcinku to {najglosniejszy2[1]} (głośność: {najglosniejszy2[0]}).")
    print(f"{najglosniejszy2[1]} wydaje rozkaz: „strzały na cięciwy – naciągnąć cięciwy – strzał!”")