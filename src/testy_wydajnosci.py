import time
import random
from modele import Krasnal, Zloze
from przydzial_pracy import MenadzerPrzydzialu
from otoczka import get_convex_hull

def generuj_duze_dane(n_krasnali, n_zloz):
    krasnale = []
    for i in range(n_krasnali):
        fachy = [f"Z{random.randint(1, n_zloz)}" for _ in range(random.randint(1, 3))]
        krasnale.append(Krasnal(f"K{i}", f"K{i}", list(set(fachy))))
    
    zloza = [Zloze(f"Z{i}", f"Z{i}", random.randint(1, 5)) for i in range(1, n_zloz + 1)]
    return krasnale, zloza

def przeprowadz_benchmark_mcmf():
    proby = [(100, 50), (1000, 500), (5000, 1000), (10000, 2000), (20000, 4000)]
    
    print("\n--- BENCHMARK PRZYDZIAŁU (EDMONDS-KARP) ---")
    print(f"{'Krasnale':>10} | {'Zloza':>10} | {'Czas [s]':>12} | {'Wynik':>10}")
    print("-" * 50)
    
    for n_k, n_z in proby:
        krasnale, zloza = generuj_duze_dane(n_k, n_z)
        menadzer = MenadzerPrzydzialu(krasnale, zloza)
        menadzer.buduj_siec()
        
        start = time.time()
        wynik = menadzer.oblicz_maksymalne_wydobycie()
        koniec = time.time()
        
        print(f"{n_k:10d} | {n_z:10d} | {koniec-start:12.4f} | {wynik:10d}")

def przeprowadz_benchmark_otoczki():
    proby = [1000, 10000, 100000, 500000, 1000000]
    
    print("\n--- BENCHMARK GEOMETRII (OTOCZKA WYPUKŁA) ---")
    print(f"{'Zloza (N)':>15} | {'Czas [s]':>12} | {'Rozmiar otoczki':>15}")
    print("-" * 50)
    
    for n in proby:
        # Generujemy N losowych punktów na płaszczyźnie 1000x1000
        punkty = [(random.uniform(0, 1000), random.uniform(0, 1000)) for _ in range(n)]
        
        start = time.time()
        otoczka = get_convex_hull(punkty)
        koniec = time.time()
        
        print(f"{n:15d} | {koniec-start:12.4f} | {len(otoczka):15d}")

if __name__ == "__main__":
    print("=== ROZPOCZĘCIE TESTÓW WYDAJNOŚCIOWYCH ===")
    przeprowadz_benchmark_mcmf()
    przeprowadz_benchmark_otoczki()