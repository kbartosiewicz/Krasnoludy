class Krasnal:
    def __init__(self, id_krasnala, imie, umiejetnosci):
        self.id_krasnala = id_krasnala
        self.imie = imie
        self.umiejetnosci = umiejetnosci  # Lista minerałów, które potrafi wydobywać

class Zloze:
    def __init__(self, id_zloza, nazwa, wydajnosc, x=0.0, y=0.0):
        self.id_zloza = id_zloza
        self.nazwa = nazwa
        self.wydajnosc = wydajnosc  # Ilu krasnali może tu pracować 
        self.x = x  # DODANE DO OTOCZKI
        self.y = y  # DODANE DO OTOCZKI