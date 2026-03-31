class Krawedz:
    def __init__(self, cel, przepustowosc, koszt=0):
        self.cel = cel      # Wierzchołek docelowy
        self.przepustowosc = przepustowosc
        self.przeplyw = 0
        self.koszt = koszt  # Tu jest miejsce na odległość
        self.odwrotna = None    # Wskaźnik na krawędź odwrotną (obiekt typu Krawedz)

class SiecPrzeplywowa:
    def __init__(self):
        self.sasiedztwo = {}    # Słownik reprezentujący listę sąsiedztwa grafu. Klucz to nazwa wierzchołka, a wartość to lista obiektów Krawedz wychodzących z niego.

    def dodaj_krawedz(self, start, cel, pojemnosc, koszt=0):
        prosta = Krawedz(cel, pojemnosc, koszt)
        wsteczna = Krawedz(start, 0, -koszt)
        prosta.odwrotna = wsteczna
        wsteczna.odwrotna = prosta
        self.sasiedztwo.setdefault(start, []).append(prosta)
        self.sasiedztwo.setdefault(cel, []).append(wsteczna)