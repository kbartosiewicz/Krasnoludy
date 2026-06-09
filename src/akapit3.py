import os
from modele import Krasnal, Zloze
from przydzial_pracy import MenadzerPrzydzialu
from otoczka import get_convex_hull, calculate_perimeter
from main import zaladuj_dane


if __name__ == "__main__":
    krasnale, zloza, tabela_odl = zaladuj_dane("dane.json")

    print("=== AKAPIT 3 – TRASA PATROLU KSIĘCIA (OTOCZKA WYPUKŁA) ===")
    menadzer = MenadzerPrzydzialu(krasnale, zloza, tabela_odl)
    menadzer.buduj_siec()
    menadzer.oblicz_mcmf()

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