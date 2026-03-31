class Krasnal:
    def __init__(self, id_krasnala, umiejetnosci):
        self.id_krasnala = id_krasnala
        self.umiejetnosci = umiejetnosci  # Lista minerałów, które potrafi wydobywać

class Zloze:
    def __init__(self, nazwa, wydajnosc):
        self.nazwa = nazwa
        self.wydajnosc = wydajnosc  # Ilu krasnali może tu pracować 