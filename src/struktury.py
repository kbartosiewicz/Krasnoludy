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

class DrzewoPrzedzialowe:
    def __init__(self, tablica_dekametrowcow):
        
        #tablica_dekametrowcow: Lista krotek w formacie (glosnosc, imie_krasnala)
        self.A = tablica_dekametrowcow
        self.n = len(self.A)
        # Drzewo przedziałowe implementowane na tablicy potrzebuje rozmiaru około 4 * N
        self.tree = [None] * (4 * self.n)
        
        # Element neutralny dla funkcji szukającej maksimum to minus nieskończoność
        self.e = (float('-inf'), None)
        
        if self.n > 0:
            # Wykład zakłada indeksowanie 1..n w pythonie używamy 0..n-1
            self.build(1, 0, self.n - 1)

    def f(self, x, y):
        #Funkcja f z wykładu
        # x i y to krotki: (glosnosc, imie_krasnala) porównujemy po indeksie 0 (glosnosc)
        if x[0] > y[0]:
            return x
        else:
            return y

    def build(self, v, l, r):
        #Procedura BUILD z wykładu, budująca poddrzewo
        # jeśli (l == r) to tree[v] = A[l]
        if l == r:
            self.tree[v] = self.A[l]
        else:
            # a) mid = floor((l + r) / 2)
            mid = (l + r) // 2
            
            # W reprezentacji tablicowej lewe dziecko to 2*v, prawe to 2*v + 1
            # b) BUILD(v.left, l, mid, f)
            self.build(2 * v, l, mid)
            
            # c) BUILD(v.right, mid + 1, r, f)
            self.build(2 * v + 1, mid + 1, r)
            
            # d) tree[v] = f(tree[v.left], tree[v.right])
            self.tree[v] = self.f(self.tree[2 * v], self.tree[2 * v + 1])

    def _query(self, v, l, r, ql, qr):
        #Procedura QUERY z wykładu
        # 1) jeśli (r < ql lub qr < l) to zwróć e (element neutralny)
        if r < ql or qr < l:
            return self.e
        
        # 2) jeśli (ql <= l oraz r <= qr) to zwróć tree[v]
        if ql <= l and r <= qr:
            return self.tree[v]
        
        # else wykonaj a, b, c, d
        # a) mid = floor((l + r) / 2)
        mid = (l + r) // 2
        
        # b) x = QUERY(...)
        x = self._query(2 * v, l, mid, ql, qr)
        
        # c) y = QUERY(...)
        y = self._query(2 * v + 1, mid + 1, r, ql, qr)
        
        # d) zwróć f(x, y)
        return self.f(x, y)

    def znajdz_najglosniejszego(self, poczatek, koniec):
        # Funkcja pomocnicza do wywoływania zapytań przez użytkownika
        # poczatek i koniec to metry granicy (indeksy tablicy)
        wynik = self._query(1, 0, self.n - 1, poczatek, koniec)
        return wynik