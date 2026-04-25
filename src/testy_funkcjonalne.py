from modele import Krasnal, Zloze
from przydzial_pracy import MenadzerPrzydzialu

def uruchom_test(nazwa, krasnale, zloza, oczekiwany_wynik):
    print(f"Uruchamianie: {nazwa}...", end=" ")
    menadzer = MenadzerPrzydzialu(krasnale, zloza)
    menadzer.buduj_siec()
    wynik = menadzer.oblicz_maksymalne_wydobycie()
    
    if wynik == oczekiwany_wynik:
        print("✅ SUKCES")
        return True
    else:
        print(f"❌ BŁĄD (Dostałem {wynik}, oczekiwałem {oczekiwany_wynik})")
        return False

# --- DEFINICJE TESTÓW ---

def testy_podstawowe():
    # Test 10x10: Każdy ma swój unikalny fach
    k, z = ([Krasnal(f"K{i}", f"Tomek{i}", [f"Z{i}"]) for i in range(1, 11)],
            [Zloze(f"Z{i}", f"Zloze{i}", 1) for i in range(1, 11)])
    uruchom_test("Test 10x10 (Pełne dopasowanie)", k, z, 10)

    # Test 100x50: Nadmiar krasnali, limit złóż
    k, z = ([Krasnal(f"K{i}", f"K{i}", [f"Z{(i%50)+1}"]) for i in range(1, 101)],
            [Zloze(f"Z{i}", f"Z{i}", 1) for i in range(1, 51)])
    uruchom_test("Test 100x50 (Limit wydajności złóż)", k, z, 50)

def testy_brzegowe():
    # TB1: Brak krasnali
    uruchom_test("TB1: Brak krasnali", [], [Zloze("Z1", "Z1", 5)], 0)

    # TB2: Obcy Fach (Rozszerzenie 1.A)
    k, z = ([Krasnal("K1", "Gimli", ["Diamenty"])], [Zloze("Z1", "Zloto", 1)])
    uruchom_test("TB2: Obcy Fach", k, z, 0)

    # TB3: Wydajność zero
    k, z = ([Krasnal("K1", "Balin", ["Z1"])], [Zloze("Z1", "Z1", 0)])
    uruchom_test("TB3: Złoże o wydajności 0", k, z, 0)

    # TB4: Nadmiar pracowników (Weryfikowalność poprawności)
    k, z = ([Krasnal(f"K{i}", f"K{i}", ["Z1"]) for i in range(5)], 
            [Zloze("Z1", "Z1", 2)])
    uruchom_test("TB4: 5 krasnali na 2 miejsca", k, z, 2)

if __name__ == "__main__":
    print("=== ROZPOCZĘCIE TESTÓW FUNKCJONALNYCH ===\n")
    testy_podstawowe()
    testy_brzegowe()
    print("\n=== TESTY ZAKOŃCZONE ===")