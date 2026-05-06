import json
from modele import Krasnal, Zloze
from przydzial_pracy import MenadzerPrzydzialu
from otoczka import get_convex_hull, calculate_perimeter

def zaladuj_dane(plik):
    with open(plik, 'r', encoding='utf-8') as f:
        dane = json.load(f)
    
    krasnale = [Krasnal(k['id'], k['imie'], k['umiejetnosci']) for k in dane['krasnale']]
    
    # ZMIANA 1: Dodane pobieranie x i y. Używamy .get(), by uniknąć błędu 
    # jeśli w starych danych nie będzie wpisanych współrzędnych.
    zloza = [Zloze(z['id'], z['nazwa'], z['wydajnosc'], z.get('x', 0.0), z.get('y', 0.0)) for z in dane['zloza']]
    
    tabela_odl = {}
    for o in dane['odleglosci']:
        tabela_odl[(o['krasnal'], o['zloze'])] = o['wartosc']
        
    return krasnale, zloza, tabela_odl

# Użycie:
krasnale, zloza, tabela_odl = zaladuj_dane('src/dane.json')
menadzer = MenadzerPrzydzialu(krasnale, zloza, tabela_odl)

# Zbudowanie sieci i znalezienie rozwiązania (Kod chłopaków)
menadzer.buduj_siec()
przeplyw, koszt = menadzer.oblicz_mcmf()

print("=== RAPORT PRZYDZIAŁU ===")
print(f"Ilość pracujących krasnali (max przepływ): {przeplyw}")
print(f"Łączny pokonany dystans (min koszt): {koszt}")

# ZMIANA 2: Odpalenie Twojej części (Otoczka Wypukła)
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