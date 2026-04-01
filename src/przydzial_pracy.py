from collections import deque
from modele import Krasnal, Zloze
from struktury import SiecPrzeplywowa

class MenadzerPrzydzialu:
    def __init__(self, lista_krasnali, lista_zloz):
        self.krasnale = lista_krasnali
        self.zloza = lista_zloz
        self.siec = SiecPrzeplywowa()
        self.zrodlo = "START"   # sztuczne źródło S, przepływ stąd wypływa
        self.ujscie = "KONIEC"  # sztuczne ujście T, a tutaj ten przypływ wpływa

    def buduj_siec(self):
        """Implementuje wymagania: krasnale do złóż zgodnie z ich umiejetnosciami."""
        for k in self.krasnale:
            # Każdy krasnal to 1 jednostka pracy
            self.siec.dodaj_krawedz(self.zrodlo, k.id_krasnala, 1)
            for fach in k.umiejetnosci:
                self.siec.dodaj_krawedz(k.id_krasnala, fach, 1)

        for z in self.zloza:
            # Złoże przyjmuje tylu krasnali, ile wynosi wydajność
            self.siec.dodaj_krawedz(z.nazwa, self.ujscie, z.wydajnosc)

    def oblicz_maksymalne_wydobycie(self):
        """Implementacja algorytmu Edmondsa-Karpa."""
        przeplyw_calkowity = 0
        while True:
            rodzic = {self.zrodlo: None}
            krawedz_do = {}
            kolejka = deque([self.zrodlo])
            
            # Szukanie ścieżki (BFS)
            while kolejka:
                u = kolejka.popleft()
                if u == self.ujscie: break
                for krawedz in self.siec.sasiedztwo.get(u, []):
                    if krawedz.przepustowosc - krawedz.przeplyw > 0 and krawedz.cel not in rodzic:
                        rodzic[krawedz.cel] = u
                        krawedz_do[krawedz.cel] = krawedz
                        kolejka.append(krawedz.cel)
            else: break # Brak ścieżki

            przeplyw_calkowity += 1
            aktualny = self.ujscie
            while aktualny != self.zrodlo:
                e = krawedz_do[aktualny]
                e.przeplyw += 1
                e.odwrotna.przeplyw -= 1
                aktualny = rodzic[aktualny]
        return przeplyw_calkowity 