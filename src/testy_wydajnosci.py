import time
import random
from modele import Krasnal, Zloze
from przydzial_pracy import MenadzerPrzydzialu

def generuj_duze_dane(n_krasnali, n_zloz):
    krasnale = []
    for i in range(n_krasnali):
        # Każdy krasnal zna od 1 do 3 losowych fachów
        fachy = [f"Z{random.randint(1, n_zloz)}" for _ in range(random.randint(1, 3))]
        krasnale.append(Krasnal(f"K{i}", f"K{i}", list(set(fachy))))
    
    zloza = [Zloze(f"Z{i}", f"Z{i}", random.randint(1, 5)) for i in range(1, n_zloz + 1)]
    return krasnale, zloza

def przeprowadz_benchmark():
    proby = [
        (100, 50), 
        (1000, 500), 
        (5000, 1000), 
        (10000, 2000), 
        (20000, 4000)
    ]
    
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

if __name__ == "__main__":
    przeprowadz_benchmark()