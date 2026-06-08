import time
import random
import matplotlib.pyplot as plt
from struktury import DrzewoPrzedzialowe

def test_wydajnosci_drzewa():
    # rozmiary granicy (liczba krasnoludków)
    rozmiary_N = [10000, 50000, 100000, 500000, 1000000]
    czasy_zapytan = []
    liczba_zapytan_testowych = 10000 # 10k ataków do przetestowania

    for N in rozmiary_N:
        # generowanie losowej granicy (glosnosc, imie)
        tablica_granicy = [(random.randint(1, 100), f"Krasnal_{i}") for i in range(N)]
        
        # budowa drzewa
        drzewo = DrzewoPrzedzialowe(tablica_granicy)
        
        # generowanie losowych przedziałów ataków
        zapytania = []
        for _ in range(liczba_zapytan_testowych):
            poczatek = random.randint(0, N - 2)
            koniec = random.randint(poczatek + 1, N - 1)
            zapytania.append((poczatek, koniec))
            
        # mierzymy czas wykonania zapytań - obrony przed atakami
        start = time.time()
        for poczatek, koniec in zapytania:
            drzewo.znajdz_najglosniejszego(poczatek, koniec)
        koniec_czasu = time.time()
        
        czas_calkowity = koniec_czasu - start
        czasy_zapytan.append(czas_calkowity)
        print(f"N: {N} | Czas dla 10 000 ataków: {czas_calkowity:.4f} s")

    # wykres wydajności
    plt.figure(figsize=(10, 6))
    plt.plot(rozmiary_N, czasy_zapytan, marker='o', linestyle='-', color='#1f77b4')
    
    for i, txt in enumerate(rozmiary_N):
        plt.annotate(f"N:{txt}", (rozmiary_N[i], czasy_zapytan[i]), 
                     textcoords="offset points", xytext=(0,10), ha='center',
                     bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", lw=0.5))

    plt.title('Wydajność algorytmu Drzewa Przedziałowego - czas 10 000 ataków')
    plt.xlabel('Liczba krasnoludków na granicy (N)')
    plt.ylabel('Czas obliczeń (s)')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.savefig('wykres_dekametrowcy.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == '__main__':
    test_wydajnosci_drzewa()