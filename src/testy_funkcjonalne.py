from modele import Krasnal, Zloze
from przydzial_pracy import MenadzerPrzydzialu
import math
from otoczka import get_convex_hull, calculate_perimeter
from struktury import KompresorKsiag

def uruchom_test(nazwa, krasnale, zloza, oczekiwany_wynik):
    print(f"Uruchamianie: {nazwa}...", end=" ")
    menadzer = MenadzerPrzydzialu(krasnale, zloza)
    menadzer.buduj_siec()
    wynik = menadzer.oblicz_maksymalne_wydobycie()
    
    if wynik == oczekiwany_wynik:
        print(" SUKCES")
        return True
    else:
        print(f" BŁĄD (Dostałem {wynik}, oczekiwałem {oczekiwany_wynik})")
        return False

def uruchom_test_otoczki(nazwa, punkty, oczekiwana_otoczka, oczekiwany_obwod=None):
    print(f"Uruchamianie: {nazwa}...", end=" ")
    wynik_otoczki = get_convex_hull(punkty)
    
    # Sortujemy obie listy przed porównaniem, żeby kolejność wierzchołków nie robiła błędu
    if sorted(wynik_otoczki) == sorted(oczekiwana_otoczka):
        if oczekiwany_obwod is not None:
            obwod = calculate_perimeter(wynik_otoczki)
            if math.isclose(obwod, oczekiwany_obwod, abs_tol=1e-5):
                print(" SUKCES")
            else:
                print(f" BŁĄD OBWODU (Dostałem {obwod}, oczekiwałem {oczekiwany_obwod})")
        else:
            print(" SUKCES")
    else:
        print(f" BŁĄD OTOCZKI\n  Dostałem:    {wynik_otoczki}\n  Oczekiwałem: {oczekiwana_otoczka}")

def uruchom_test_ksiegi(nazwa, tekst, wzorzec, oczekiwane_indeksy):
    print(f"Uruchamianie: {nazwa}...", end=" ")
    kompresor = KompresorKsiag()
    wynik_indeksy = kompresor.szukaj_kmp(tekst, wzorzec)
    
    if wynik_indeksy == oczekiwane_indeksy:
        print(" SUKCES")
        return True
    else:
        print(f" BŁĄD (Dostałem {wynik_indeksy}, oczekiwałem {oczekiwane_indeksy})")
        return False

# --- DEFINICJE TESTÓW ---

def testy_podstawowe():
    k, z = ([Krasnal(f"K{i}", f"Tomek{i}", [f"Z{i}"]) for i in range(1, 11)],
            [Zloze(f"Z{i}", f"Zloze{i}", 1) for i in range(1, 11)])
    uruchom_test("Test 10x10 (Pełne dopasowanie)", k, z, 10)

    k, z = ([Krasnal(f"K{i}", f"K{i}", [f"Z{(i%50)+1}"]) for i in range(1, 101)],
            [Zloze(f"Z{i}", f"Z{i}", 1) for i in range(1, 51)])
    uruchom_test("Test 100x50 (Limit wydajności złóż)", k, z, 50)

def testy_brzegowe():
    uruchom_test("TB1: Brak krasnali", [], [Zloze("Z1", "Z1", 5)], 0)
    k, z = ([Krasnal("K1", "Gimli", ["Diamenty"])], [Zloze("Z1", "Zloto", 1)])
    uruchom_test("TB2: Obcy Fach", k, z, 0)
    k, z = ([Krasnal("K1", "Balin", ["Z1"])], [Zloze("Z1", "Z1", 0)])
    uruchom_test("TB3: Złoże o wydajności 0", k, z, 0)
    k, z = ([Krasnal(f"K{i}", f"K{i}", ["Z1"]) for i in range(5)], 
            [Zloze("Z1", "Z1", 2)])
    uruchom_test("TB4: 5 krasnali na 2 miejsca", k, z, 2)

def testy_geometrii():
    p1 = [(0, 0), (2, 0), (1, 1), (2, 2), (0, 2)]
    o1 = [(0, 0), (2, 0), (2, 2), (0, 2)]
    uruchom_test_otoczki("TO1: Kwadrat z kopalnią wewnątrz", p1, o1, 8.0)

    p2 = [(1, 1), (4, 4)]
    o2 = [(1, 1), (4, 4)]
    uruchom_test_otoczki("TO2: Dwie działające kopalnie", p2, o2, 8.48528137423857)

    p3 = [(0, 0), (1, 1), (2, 2), (3, 3)]
    o3 = [(0, 0), (3, 3)]
    uruchom_test_otoczki("TO3: Kopalnie w linii prostej", p3, o3)

    p4 = [(0, 0), (4, 0), (2, 4)]
    o4 = [(0, 0), (4, 0), (2, 4)]
    uruchom_test_otoczki("TO4: Trójkąt", p4, o4, 12.94427190999916)

def testy_ksiegi():
    tekst = "ABCDBABCABBCDABCAB"
    wzorzec = "ABCAB"
    uruchom_test_ksiegi("TK1: Zwykły tekst (przykład z wykładu)", tekst, wzorzec, [5, 13])
    uruchom_test_ksiegi("TK2: Brak wzorca w tekście", tekst, "OWSIANKA", [])

if __name__ == "__main__":
    print("=== ROZPOCZĘCIE TESTÓW FUNKCJONALNYCH ===\n")
    print("--- GRAFY (PRZYDZIAŁ KRASNALI) ---")
    testy_podstawowe()
    testy_brzegowe()
    print("\n--- GEOMETRIA (OTOCZKA WYPUKŁA) ---")
    testy_geometrii()
    print("\n--- KOMPRESJA I WYSZUKIWANIE (KSIĘGI) ---")
    testy_ksiegi()
    print("\n=== TESTY ZAKOŃCZONE ===")