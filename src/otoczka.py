import math
from functools import cmp_to_key

def det(p0, pi, pj):
    """
    Wyznacznik dokładnie według wzoru ze slajdu 5 i 11.
    Ważne: p0 to wierzchołek (punkt odniesienia)[cite: 2].
    """
    return (pi[0] - p0[0]) * (pj[1] - p0[1]) - (pj[0] - p0[0]) * (pi[1] - p0[1])

def distance_sq(p1, p2):
    """Kwadrat odległości do porównywania punktów współliniowych."""
    return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2

def get_convex_hull(points):
    """Algorytm Grahama zgodny z wykładem i poprawny dla testów kwadratu."""
    if len(points) <= 3:
        return list(set(points))

    # KROK 1: Wybierz punkt p0 (najmniejsze y, potem najmniejsze x).
    p0 = min(points, key=lambda p: (p[1], p[0]))

    # KROK 2: Sortowanie kątowe bez trygonometrii.
    def compare_angles(p1, p2):
        if p1 == p0: return -1
        if p2 == p0: return 1
        d = det(p0, p1, p2)
        if d > 0: return -1  # p1 ma mniejszą współrzędną kątową
        if d < 0: return 1   # p2 ma mniejszą współrzędną kątową
        # Dla współliniowych: bliższy punkt pierwszy
        return -1 if distance_sq(p0, p1) < distance_sq(p0, p2) else 1

    posortowane = sorted(points, key=cmp_to_key(compare_angles))

    # KROK 3: Usuwanie bliższych punktów współliniowych.
    unikalne_punkty = [posortowane[0]]
    for i in range(1, len(posortowane)):
        if i < len(posortowane) - 1 and det(p0, posortowane[i], posortowane[i+1]) == 0:
            continue
        unikalne_punkty.append(posortowane[i])

    if len(unikalne_punkty) < 3:
        return unikalne_punkty

    # KROK 4: Inicjalizacja stosu.
    stos = [unikalne_punkty[0], unikalne_punkty[1], unikalne_punkty[2]]

    # KROK 5: Główna pętla Grahama.
    for i in range(3, len(unikalne_punkty)):
        pi = unikalne_punkty[i]
        # Ważna zmiana: det(TOP, NEXT-TO-TOP, pi).
        # Zgodnie z wykładem, p0 (pierwszy argument) to wierzchołek skrętu.
        # Skręt w lewo jest gdy det < 0, więc dopóki det >= 0, robimy POP.
        while len(stos) >= 2 and det(stos[-1], stos[-2], pi) >= 0:
            stos.pop()
        stos.append(pi)

    return stos

def calculate_perimeter(hull_points):
    """Oblicza sumaryczną długość trasy (obwód) dla patrolu księcia[cite: 1]."""
    if len(hull_points) < 2:
        return 0.0
    
    perimeter = 0.0
    for i in range(len(hull_points)):
        p1 = hull_points[i]
        p2 = hull_points[(i + 1) % len(hull_points)]
        perimeter += math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        
    return perimeter