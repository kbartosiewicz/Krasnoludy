import os
from modele import Krasnal, Zloze
from przydzial_pracy import MenadzerPrzydzialu
from struktury import SiecPrzeplywowa
from main import zaladuj_dane


class MenadzerPrzydzialuBezKosztu(MenadzerPrzydzialu):
    """Akapit 1 – wersja tylko z maksymalnym przepływem (bez kosztów)."""

    def __init__(self, lista_krasnali, lista_zloz):
        super().__init__(lista_krasnali, lista_zloz, tabela_odleglosci={})

    def buduj_siec(self):
        # nadpisujemy: wszystkie koszty ustawiamy na 0
        self.siec = SiecPrzeplywowa()
        for k in self.krasnale:
            self.siec.dodaj_krawedz(self.zrodlo, k.id_krasnala, 1, koszt=0)
            for fach in k.umiejetnosci:
                self.siec.dodaj_krawedz(k.id_krasnala, fach, 1, koszt=0)
        for z in self.zloza:
            self.siec.dodaj_krawedz(z.id_zloza, self.ujscie, z.wydajnosc, koszt=0)


if __name__ == "__main__":
    krasnale, zloza, tabela_odl = zaladuj_dane("dane.json")

    print("=== AKAPIT 1 – MAKSYMALNA LICZBA PRACUJĄCYCH KRASNALI (BEZ DYSTANSÓW) ===")
    menadzer = MenadzerPrzydzialuBezKosztu(krasnale, zloza)
    menadzer.buduj_siec()
    przeplyw, _ = menadzer.oblicz_mcmf()
    print(f"Liczba pracujących krasnali (max przepływ): {przeplyw}")