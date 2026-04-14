import json
from modele import Krasnal, Zloze
from przydzial_pracy import MenadzerPrzydzialu

def zaladuj_dane(plik):
    with open(plik, 'r', encoding='utf-8') as f:
        dane = json.load(f)
    
    krasnale = [Krasnal(k['imie'], k['id'], k['umiejetnosci']) for k in dane['krasnale']]
    zloza = [Zloze(z['id'], z['nazwa'], z['wydajnosc']) for z in dane['zloza']]
    
    tabela_odl = {}
    for o in dane['odleglosci']:
        tabela_odl[(o['krasnal'], o['zloze'])] = o['wartosc']
        
    return krasnale, zloza, tabela_odl

# Użycie:
krasnale, zloza, tabela_odl = zaladuj_dane('src/dane.json')
menadzer = MenadzerPrzydzialu(krasnale, zloza, tabela_odl)

# Zbudowanie sieci i znalezienie rozwiązania
menadzer.buduj_siec()
przeplyw, koszt = menadzer.oblicz_mcmf()

print(f"Ilość pracujących krasnali (max przepływ): {przeplyw}")
print(f"Łączny pokonany dystans (min koszt): {koszt}")