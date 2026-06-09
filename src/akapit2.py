import os
from modele import Krasnal, Zloze
from przydzial_pracy import MenadzerPrzydzialu
from main import zaladuj_dane


if __name__ == "__main__":
    krasnale, zloza, tabela_odl = zaladuj_dane("dane.json")

    print("=== AKAPIT 2 – MINIMALNY ŁĄCZNY DYSTANS PRZY ZACHOWANIU PRODUKCJI ===")
    menadzer = MenadzerPrzydzialu(krasnale, zloza, tabela_odl)
    menadzer.buduj_siec()
    przeplyw, koszt = menadzer.oblicz_mcmf()
    print(f"Liczba pracujących krasnali (max przepływ): {przeplyw}")
    print(f"Łączny pokonany dystans (min koszt): {koszt}")