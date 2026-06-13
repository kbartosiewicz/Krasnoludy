from struktury import KompresorKsiag

if __name__ == "__main__":
    print("=== AKAPIT 5 – KOMPRESJA KSIĄG I BŁYSKAWICZNE WYSZUKIWANIE ===")
    kompresor = KompresorKsiag()
    
    tekst_ksiegi = "Królewna Śnieżka gotuje dużo owsianki. Ta owsianka jest bardzo zdrowa."
    print(f"Oryginalny tekst zajmuje znaków: {len(tekst_ksiegi)}")
    
    # Kompresja
    skompresowany, korzen = kompresor.kompresuj_tekst(tekst_ksiegi)
    print(f"Skompresowany tekst (bity): {skompresowany}")
    print(f"Rozmiar po kompresji: {len(skompresowany)} bitów")
    
    # Wyszukiwanie KMP
    szukane_slowo = "owsianki"
    pozycje = kompresor.szukaj_kmp(tekst_ksiegi.lower(), szukane_slowo.lower())
    print(f"\nSzukane słowo: '{szukane_slowo}'")
    if pozycje:
        print(f"Znaleziono na indeksach: {pozycje}")
    else:
        print("Nie znaleziono słowa w księdze.")