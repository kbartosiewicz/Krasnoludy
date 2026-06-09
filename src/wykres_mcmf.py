import time
import random
import matplotlib.pyplot as plt
from modele import Krasnal, Zloze
from przydzial_pracy import MenadzerPrzydzialu

def generuj_duze_dane(n_krasnali, n_zloz):
    krasnale = []
    for i in range(n_krasnali):
        fachy = [f"Z{random.randint(1, n_zloz)}" for _ in range(random.randint(1, 3))]
        krasnale.append(Krasnal(f"K{i}", f"K{i}", list(set(fachy))))

    zloza = [Zloze(f"Z{i}", f"Z{i}", random.randint(1, 5)) for i in range(1, n_zloz + 1)]
    return krasnale, zloza

def test_wydajnosci_mcmf():
    rozmiary_N = [100, 500, 1000, 2500, 5000, 10000, 20000]
    rozmiary_Z = [50, 250, 500, 750, 1000, 2000, 4000]
    czasy_zapytan = []

    print("\n--- BENCHMARK PRZYDZIAŁU (MCMF) ---")
    print(f"{'Krasnale':>10} | {'Zloza':>10} | {'Czas [s]':>12}")
    print("-" * 38)

    for n_k, n_z in zip(rozmiary_N, rozmiary_Z):
        krasnale, zloza = generuj_duze_dane(n_k, n_z)

        menadzer = MenadzerPrzydzialu(krasnale, zloza)
        menadzer.buduj_siec()

        start = time.time()
        przeplyw, koszt = menadzer.oblicz_mcmf()
        koniec = time.time()

        czas_calkowity = koniec - start
        czasy_zapytan.append(czas_calkowity)
        print(f"{n_k:10d} | {n_z:10d} | {czas_calkowity:12.4f}s")

    plt.figure(figsize=(10, 6))

    plt.plot(rozmiary_N, czasy_zapytan, marker='o', linestyle='-', color='#d62728', linewidth=2)
    plt.xscale('log')
    plt.xticks(rozmiary_N, [str(x) for x in rozmiary_N])

    for i, txt in enumerate(rozmiary_N):
        plt.annotate(
            f"K:{txt}\nZ:{rozmiary_Z[i]}",
            (rozmiary_N[i], czasy_zapytan[i]),
            textcoords="offset points",
            xytext=(0, 15),
            ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", lw=0.5)
        )

    plt.title('Wydajność algorytmu MCMF w zależności od rozmiaru danych', fontsize=14)
    plt.xlabel('Liczba krasnoludków (K) - Skala logarytmiczna', fontsize=12)
    plt.ylabel('Czas obliczeń (s)', fontsize=12)
    plt.grid(True, which="both", linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig('wykres_mcmf.png', dpi=300, bbox_inches='tight')
    print("Wykres został zapisany jako 'wykres_mcmf.png'.")
    plt.show()

if __name__ == '__main__':
    test_wydajnosci_mcmf()
