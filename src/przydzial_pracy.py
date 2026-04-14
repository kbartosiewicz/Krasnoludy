from collections import deque
from modele import Krasnal, Zloze
from struktury import SiecPrzeplywowa

class MenadzerPrzydzialu:
    def __init__(self, lista_krasnali, lista_zloz, tabela_odleglosci=None):
        self.krasnale = lista_krasnali
        self.zloza = lista_zloz
        self.tabela_odleglosci = tabela_odleglosci or {}
        self.siec = SiecPrzeplywowa()
        self.zrodlo = "START"   # sztuczne źródło S, przepływ stąd wypływa
        self.ujscie = "KONIEC"  # sztuczne ujście T, a tutaj ten przypływ wpływa

    def buduj_siec(self):
        """Implementuje wymagania: krasnale do złóż zgodnie z ich umiejetnosciami."""
        for k in self.krasnale:
            # Każdy krasnal to 1 jednostka pracy
            self.siec.dodaj_krawedz(self.zrodlo, k.id_krasnala, 1)
            for fach in k.umiejetnosci:
                koszt = self.tabela_odleglosci.get((k.id_krasnala, fach), 0)
                self.siec.dodaj_krawedz(k.id_krasnala, fach, 1, koszt)

        for z in self.zloza:
            # Złoże przyjmuje tylu krasnali, ile wynosi wydajność
            self.siec.dodaj_krawedz(z.id_zloza, self.ujscie, z.wydajnosc)

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
    
    def oblicz_mcmf(self):
        przeplyw_calkowity = 0
        koszt_calkowity = 0

        while True:
            # Inicjalizacja struktur dla SPFA
            # Ustawiamy odległość do wszystkich znanych wierzchołków na nieskończoność
            odleglosci = {wierzcholek: float('inf') for wierzcholek in self.siec.sasiedztwo}
            odleglosci[self.zrodlo] = 0
            
            # Upewniamy się, że ujście jest w słowniku
            if self.ujscie not in odleglosci:
                odleglosci[self.ujscie] = float('inf')

            rodzic = {self.zrodlo: None}
            krawedz_do = {}
            kolejka = deque([self.zrodlo])
            w_kolejce = {self.zrodlo} # Zbiór (set) pozwala na szybkie sprawdzanie O(1)

            # Szukanie najtańszej ścieżki powiększającej (SPFA)
            while kolejka:
                u = kolejka.popleft()
                w_kolejce.remove(u)

                for krawedz in self.siec.sasiedztwo.get(u, []):
                    # Warunek: krawędź musi mieć wolną przepustowość
                    if krawedz.przepustowosc - krawedz.przeplyw > 0:
                        nowy_koszt = odleglosci[u] + krawedz.koszt
                        
                        # Zabezpieczenie, jeśli wierzchołka docelowego nie było jeszcze w słowniku
                        if krawedz.cel not in odleglosci:
                            odleglosci[krawedz.cel] = float('inf')

                        # Relaksacja krawędzi: jeśli znaleźliśmy tańszą ścieżkę do 'cel'
                        if nowy_koszt < odleglosci[krawedz.cel]:
                            odleglosci[krawedz.cel] = nowy_koszt
                            rodzic[krawedz.cel] = u
                            krawedz_do[krawedz.cel] = krawedz

                            # Jeśli wierzchołka nie ma w kolejce, dodajemy go, by sprawdzić jego sąsiadów
                            if krawedz.cel not in w_kolejce:
                                kolejka.append(krawedz.cel)
                                w_kolejce.add(krawedz.cel)

            # Warunek stopu: Jeśli odległość do ujścia to wciąż nieskończoność, brak ścieżek
            if odleglosci.get(self.ujscie, float('inf')) == float('inf'):
                break

            # Aktualizacja przepływu i kosztu na znalezionej ścieżce
            # Ponieważ każdy krasnal to 1 jednostka przepływu, pchamy dokładnie 1.
            przeplyw_calkowity += 1
            aktualny = self.ujscie
            
            while aktualny != self.zrodlo:
                e = krawedz_do[aktualny]
                e.przeplyw += 1
                e.odwrotna.przeplyw -= 1
                koszt_calkowity += e.koszt  # Dodajemy odległość pokonaną na tym odcinku
                aktualny = rodzic[aktualny]

        return przeplyw_calkowity, koszt_calkowity