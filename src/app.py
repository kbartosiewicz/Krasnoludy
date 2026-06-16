import streamlit as st
import networkx as nx
import random
import json
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from pyvis.network import Network

from modele import Krasnal, Zloze
from przydzial_pracy import MenadzerPrzydzialu
from otoczka import get_convex_hull, calculate_perimeter
from struktury import DrzewoPrzedzialowe, KompresorKsiag
import matplotlib.pyplot as plt

# Konfiguracja strony Streamlit
st.set_page_config(page_title="Królestwo Krasnali - Panel Dowodzenia", layout="wide")

st.title("🏰 Królewski Panel Sterowania Królestwem Krasnali")
st.write("Profesjonalny system zarządzania królestwem w czasie rzeczywistym.")

# ==========================================
# INICJALIZACJA KLUCZA SESJI WIDŻETÓW I PUSTEGO STANU
# ==========================================
if 'form_key' not in st.session_state:
    st.session_state.form_key = 0

if 'krasnale_m1' not in st.session_state:
    st.session_state.krasnale_m1 = []
    st.session_state.zloza_m1 = []
    st.session_state.tabela_odl = {}

# ==========================================
# FUNKCJE ZARZĄDZANIA DANYMI
# ==========================================
def wyczysc_stare_widzety():
    st.session_state.form_key += 1

def zaladuj_dane_z_pliku(dane_json):
    wyczysc_stare_widzety()
    st.session_state.zloza_m1 = [Zloze(z['id'], z['nazwa'], z['wydajnosc'], z.get('x', 0.0), z.get('y', 0.0)) for z in dane_json['zloza']]
    st.session_state.krasnale_m1 = [Krasnal(k['id'], k['imie'], k['umiejetnosci'], k.get('glosnosc', 50)) for k in dane_json['krasnale']]
    st.session_state.tabela_odl = {}
    for odl in dane_json.get('odleglosci', []):
        st.session_state.tabela_odl[(odl['krasnal'], odl['zloze'])] = odl['wartosc']

    for k in st.session_state.krasnale_m1:
        k.umiejetnosci = [fach for fach in k.umiejetnosci if (k.id_krasnala, fach) in st.session_state.tabela_odl]

def generuj_losowe_dane():
    wyczysc_stare_widzety()
    
    liczba_zloz = random.randint(0, 10)
    liczba_krasnali = random.randint(7, 30) 
    
    st.session_state.zloza_m1 = []
    zloza_ids = []
    for i in range(1, liczba_zloz + 1):
        zid = f"Z{i}"
        zloza_ids.append(zid)
        wydajnosc = random.randint(0, 10)
        x = round(random.uniform(-50.0, 50.0), 1)
        y = round(random.uniform(-50.0, 50.0), 1)
        st.session_state.zloza_m1.append(Zloze(zid, f"Kopalnia_{zid}", wydajnosc, x, y))
        
    st.session_state.krasnale_m1 = []
    st.session_state.tabela_odl = {}
    
    imiona_baza = ["Gimli", "Thorin", "Balin", "Dwalin", "Kili", "Fili", "Oin", "Gloin", "Dori", "Nori", "Ori", "Bifur", "Bofur", "Bombur", "Durin", "Dain", "Thror", "Thrain", "Nain", "Fundin"]
    
    for i in range(1, liczba_krasnali + 1):
        kid = f"K{i}"
        imie = imiona_baza[i-1] if i-1 < len(imiona_baza) else f"Krasnal_{i}"
        glosnosc = random.randint(0, 150)
        
        ilosc_fachow = random.randint(0, liczba_zloz)
        fachy = random.sample(zloza_ids, ilosc_fachow)
        
        st.session_state.krasnale_m1.append(Krasnal(kid, imie, fachy, glosnosc))
        
        for fach in fachy:
            st.session_state.tabela_odl[(kid, fach)] = random.randint(1, 50)

# ==========================================
# MENU BOCZNE I OBSŁUGA PLIKÓW
# ==========================================
st.sidebar.markdown("---")
modul = st.sidebar.radio(
    "Wybierz moduł królestwa:",
    ["⚒️ Moduł I: Przydział Pracy (Algorytm MCMF)", 
     "🐎 Moduł II: Patrol Księcia (Otoczka wypukła)", 
     "🛡️ Moduł III: Obrona Granic (Wybór dekametrowca)",
     "📜 Moduł IV: Królewskie Archiwum (KMP i Huffman)"],
    key="wybrany_modul"
)
st.sidebar.markdown("---")

st.sidebar.header("📁 Źródło Danych")
wgrany_plik = st.sidebar.file_uploader("Wgraj własny plik JSON", type=["json"])

if st.sidebar.button("Załaduj plik JSON", width='stretch'):
    if wgrany_plik is not None:
        dane_z_pliku = json.load(wgrany_plik)
        zaladuj_dane_z_pliku(dane_z_pliku)
        st.rerun() 
    else:
        st.sidebar.error("Najpierw wybierz plik!")

st.sidebar.markdown("lub")

if st.sidebar.button("🎲 Wygeneruj losowe dane", width='stretch'):
    generuj_losowe_dane()
    st.rerun()
    
if len(st.session_state.krasnale_m1) > 0 or len(st.session_state.zloza_m1) > 0:
    if st.sidebar.button("🗑️ Wyczyść wszystkie dane", width='stretch'):
        st.session_state.krasnale_m1 = []
        st.session_state.zloza_m1 = []
        st.session_state.tabela_odl = {}
        wyczysc_stare_widzety()
        st.rerun()

st.sidebar.markdown("---")

# ==========================================
# MODUŁ I: PRZYDZIAŁ PRACY (GRAFY)
# ==========================================
if modul == "⚒️ Moduł I: Przydział Pracy (Algorytm MCMF)":
    st.header("⚒️ Interaktywne Zarządzanie i Przydział Pracy (MCMF)")
    
    if len(st.session_state.krasnale_m1) == 0 and len(st.session_state.zloza_m1) == 0:
        st.info("👋 Witaj w Panelu Sterowania! Królestwo jest puste. Dodaj zasoby ręcznie poniżej, wgraj plik JSON lub wygeneruj losowe dane.")

    col_menu, col_graf = st.columns([1, 2])

    with col_menu:
        st.subheader("⚙️ Zarządzanie Zasobami")
        
        st.write("**--- Zarządzanie Złożami ---**")
        with st.expander("➕ Dodaj Nowe Złoże", expanded=(len(st.session_state.zloza_m1) == 0)):
            nowe_z_nazwa = st.text_input("Nazwa nowego złoża:", "Nowa Kopalnia", key=f"nowe_z_naz_{st.session_state.form_key}")
            nowe_z_wydajnosc = st.number_input("Wydajność złoża:", min_value=0, max_value=10, value=2, key=f"nowe_z_wyd_{st.session_state.form_key}")
            c_x, c_y = st.columns(2)
            nowe_z_x = c_x.number_input("Współrzędna X:", min_value=-50.0, max_value=50.0, value=5.0, step=0.5, key=f"nowe_z_x_{st.session_state.form_key}")
            nowe_z_y = c_y.number_input("Współrzędna Y:", min_value=-50.0, max_value=50.0, value=5.0, step=0.5, key=f"nowe_z_y_{st.session_state.form_key}")
            
            if st.button("Zatwierdź nowe złoże"):
                # Szukamy najwyższego numeru wśród istniejących złóż
                if not st.session_state.zloza_m1:
                    nowe_id = "Z1"
                else:
                    # Wyciągamy same liczby z ID (np. z "Z12" wyciągamy 12)
                    numery = [int(z.id_zloza[1:]) for z in st.session_state.zloza_m1 if z.id_zloza[1:].isdigit()]
                    nowy_numer = max(numery) + 1 if numery else 1
                    nowe_id = f"Z{nowy_numer}"
                st.session_state.zloza_m1.append(Zloze(nowe_id, nowe_z_nazwa, nowe_z_wydajnosc, nowe_z_x, nowe_z_y))
                st.success(f"Dodano złoże {nowe_z_nazwa}!")
                wyczysc_stare_widzety()
                st.rerun()
        
        if len(st.session_state.zloza_m1) > 0:
            st.write("**Modyfikacja istniejących złóż**")
            
            # 1. Tworzymy listę opcji do wyboru
            zloza_opcje = [f"{z.nazwa} ({z.id_zloza})" for z in st.session_state.zloza_m1]
            
            # 2. Dzielimy ekran na pole wyboru i przycisk usunięcia
            c_sel_z, c_del_z = st.columns([4, 1])
            with c_sel_z:
                wybrane_zloze_str = st.selectbox("Wybierz złoże do edycji:", zloza_opcje, key=f"sel_z_{st.session_state.form_key}")
            with c_del_z:
                st.write("<br>", unsafe_allow_html=True) # Zrównanie przycisku z polem tekstowym
                if st.button("🗑️ Usuń", key=f"del_zloze_{st.session_state.form_key}"):
                    # Wyciągamy czyste ID (np. "Z1") ze stringa
                    id_z_usun = wybrane_zloze_str.split("(")[-1].replace(")", "")
                    
                    # Usuwamy złoże z bazy
                    st.session_state.zloza_m1 = [z for z in st.session_state.zloza_m1 if z.id_zloza != id_z_usun]
                    
                    # Logika czyszcząca (usuwamy to złoże krasnalom i czyścimy tabelę odległości)
                    for k in st.session_state.krasnale_m1:
                        if id_z_usun in k.umiejetnosci:
                            k.umiejetnosci.remove(id_z_usun)
                            if (k.id_krasnala, id_z_usun) in st.session_state.tabela_odl:
                                del st.session_state.tabela_odl[(k.id_krasnala, id_z_usun)]
                    st.rerun()
            
            # 3. Sekcja edycji wydajności dla wybranego złoża
            if wybrane_zloze_str:
                id_z_edycja = wybrane_zloze_str.split("(")[-1].replace(")", "")
                wybrane_z = next((z for z in st.session_state.zloza_m1 if z.id_zloza == id_z_edycja), None)
                
                if wybrane_z:
                    nowa_wydajnosc = st.number_input(
                        "Zmień wydajność złoża: ", 
                        min_value=0, 
                        max_value=10, 
                        value=int(wybrane_z.wydajnosc), 
                        key=f"wyd_{wybrane_z.id_zloza}_{st.session_state.form_key}"
                    )
                    # Jeśli zmienimy wartość na suwaku, zapisuje się ona natychmiast w obiekcie
                    if nowa_wydajnosc != wybrane_z.wydajnosc:
                        wybrane_z.wydajnosc = nowa_wydajnosc
        
        st.write("**--- Zarządzanie Krasnalami ---**")
        with st.expander("➕ Dodaj Nowego Krasnala", expanded=(len(st.session_state.krasnale_m1) == 0)):
            nowe_imie = st.text_input("Imię nowego krasnala:", key=f"nowe_imie_{st.session_state.form_key}")
            nowa_glosnosc = st.number_input("Głośność (dB):", min_value=0, max_value=150, value=50, key=f"nowa_gl_k_{st.session_state.form_key}")
            wszystkie_zloza_ids = [z.id_zloza for z in st.session_state.zloza_m1]
            nowe_fachy = st.multiselect("Fachy nowego krasnala (Złoża z listy powyżej):", wszystkie_zloza_ids, key=f"nowe_fachy_{st.session_state.form_key}")
            
            odleglosci_nowe = {}
            if nowe_fachy:
                st.write("📍 **Określ dystans z domu krasnala do kopalni:**")
                for fach in nowe_fachy:
                    odleglosci_nowe[fach] = st.number_input(
                        f"Dystans do złoża {fach} (km):", 
                        min_value=1, max_value=500, value=10, 
                        key=f"dist_new_{fach}_{st.session_state.form_key}"
                    )
            
            if st.button("Dodaj do królestwa"):
                # Szukamy najwyższego numeru wśród istniejących krasnali
                if not st.session_state.krasnale_m1:
                    new_id = "K1"
                else:
                    # Wyciągamy same liczby z ID (np. z "K4" wyciągamy 4)
                    numery = [int(k.id_krasnala[1:]) for k in st.session_state.krasnale_m1 if k.id_krasnala[1:].isdigit()]
                    nowy_numer = max(numery) + 1 if numery else 1
                    new_id = f"K{nowy_numer}"
                
                st.session_state.krasnale_m1.append(Krasnal(new_id, nowe_imie, nowe_fachy, nowa_glosnosc))
                
                for fach in nowe_fachy:
                     st.session_state.tabela_odl[(new_id, fach)] = odleglosci_nowe[fach]
                     
                st.success(f"Dodano krasnala {nowe_imie}!")
                wyczysc_stare_widzety()
                st.rerun()

        k_id = [k.id_krasnala for k in st.session_state.krasnale_m1]
        
        if len(k_id) > 0:
            st.write("**Modyfikacja istniejących krasnali**")
            
            c_sel, c_del_k = st.columns([4, 1])
            with c_sel:
                wybrany_k_id = st.selectbox("Wybierz krasnala do edycji:", k_id, key=f"sel_k_{st.session_state.form_key}")
            with c_del_k:
                st.write("<br>", unsafe_allow_html=True)
                if st.button("🗑️ Usuń", key=f"del_krasnal_{st.session_state.form_key}"):
                    st.session_state.krasnale_m1 = [k for k in st.session_state.krasnale_m1 if k.id_krasnala != wybrany_k_id]
                    st.session_state.tabela_odl = {klucz: wartosc for klucz, wartosc in st.session_state.tabela_odl.items() if klucz[0] != wybrany_k_id}
                    st.rerun()
            
            wybrany_k = next(k for k in st.session_state.krasnale_m1 if k.id_krasnala == wybrany_k_id)

            st.write(f"Aktualne fachy ({wybrany_k.imie}): `{wybrany_k.umiejetnosci}`")
            if len(wybrany_k.umiejetnosci) == 0:
                st.warning("🦥 Ten krasnal to absolutny leń. Nie ma żadnego fachu!")
            
            wszystkie_zloza_ids = [z.id_zloza for z in st.session_state.zloza_m1]
            nowe_umiejetnosci = st.multiselect("Zmień fachy krasnala:", wszystkie_zloza_ids, default=[u for u in wybrany_k.umiejetnosci if u in wszystkie_zloza_ids], key=f"um_{wybrany_k.id_krasnala}_{st.session_state.form_key}")
            
            odleglosci_edycja = {}
            if nowe_umiejetnosci:
                st.write("📍 **Aktualizuj dystans do kopalń:**")
                for fach in nowe_umiejetnosci:
                    # Szukamy starego dystansu (jeśli krasnal już tam pracował) lub ustawiamy domyślnie 10
                    stary_dystans = st.session_state.tabela_odl.get((wybrany_k.id_krasnala, fach), 10)
                    odleglosci_edycja[fach] = st.number_input(
                        f"Dystans do złoża {fach} (km):", 
                        min_value=1, max_value=500, value=int(stary_dystans), 
                        key=f"dist_edit_{wybrany_k.id_krasnala}_{fach}_{st.session_state.form_key}"
                    )
            
            if st.button("Zatwierdź zmiany fachu"):
                # 1. Czyszczenie: Usuwamy trasy do kopalń, z których krasnal został wypisany
                dla_usuniecia = [fach for fach in wybrany_k.umiejetnosci if fach not in nowe_umiejetnosci]
                for fach in dla_usuniecia:
                    if (wybrany_k.id_krasnala, fach) in st.session_state.tabela_odl:
                        del st.session_state.tabela_odl[(wybrany_k.id_krasnala, fach)]
                
                # 2. Aktualizacja: Nadpisujemy wszystkie dystanse zgodnie z tym, co wpisał użytkownik
                for fach in nowe_umiejetnosci:
                    st.session_state.tabela_odl[(wybrany_k.id_krasnala, fach)] = odleglosci_edycja[fach]
                
                wybrany_k.umiejetnosci = nowe_umiejetnosci
                st.success(f"Zaktualizowano fachy i dystanse dla {wybrany_k.imie}!")
                st.rerun()

    with col_graf:
        st.subheader("📊 Sieć Przepływowa")
        
        if len(st.session_state.krasnale_m1) < 7:
            st.error(f"❌ W królestwie pracuje aktualnie {len(st.session_state.krasnale_m1)} krasnali. Zgodnie z prawem, aby graf rozpoczął wyliczenia, potrzeba ich minimum 7.")
        elif not st.session_state.zloza_m1:
            st.warning("Krasnale gotowi do pracy, ale nie zbudowałeś jeszcze żadnej kopalni.")
        else:
            menadzer = MenadzerPrzydzialu(st.session_state.krasnale_m1, st.session_state.zloza_m1, st.session_state.tabela_odl)
            menadzer.buduj_siec()
            
            # --- METRYKI ---
            max_przeplyw, min_koszt = menadzer.oblicz_mcmf()
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.metric(label="Maksymalnie zatrudnieni (max_flow)", value=f"{max_przeplyw} krasnali")
            with col_res2:
                st.metric(label="Łączny dystans do pracy (min_cost)", value=f"{min_koszt} km")

            # --- KONFIGURACJA GRAFU ---
            net = Network(height="700px", width="100%", directed=True, bgcolor="#ffffff", font_color="black")
            
            net.set_options("""
            var options = {
              "interaction": {
                "hover": true,
                "selectConnectedEdges": true,
                "tooltipDelay": 100
              },
              "physics": {
                "enabled": false
              },
              "edges": {
                "smooth": {
                  "type": "curvedCW",
                  "roundness": 0.1
                }
              }
            }
            """)

            # --- ROZSZERZONE WSPÓŁRZĘDNE (Lepsza czytelność) ---
            # Zwiększamy dystans X: 0 -> 400 -> 1200 -> 1600
            net.add_node("START", label="START", color="#8fdf82", x=0, y=0, size=35, shape="circle")
            net.add_node("KONIEC", label="KONIEC", color="#ff6b6b", x=1500, y=0, size=35, shape="circle")

            len_k = len(st.session_state.krasnale_m1)
            for i, k in enumerate(st.session_state.krasnale_m1):
                y_pos = (i - len_k / 2) * 85 # Większy odstęp pionowy między krasnalami
                net.add_node(k.id_krasnala, 
                            label=k.id_krasnala, 
                            title=f"👤 Imię: {k.imie}\n🔊 Głośność: {k.glosnosc} dB", 
                            color="#82c3df",
                            x=300, y=y_pos,
                            size=40,  
                            shape="circle")
            
            len_z = len(st.session_state.zloza_m1)
            for i, z in enumerate(st.session_state.zloza_m1):
                y_pos = (i - len_z / 2) * 120 # Większy odstęp pionowy między złożami
                net.add_node(z.id_zloza, 
                            label=z.id_zloza, 
                            title=f"📍 Nazwa: {z.nazwa}\n⚡ Wydajność: {z.wydajnosc}",
                            color="#dfca82",
                            x=1100, y=y_pos,
                            size=40,
                            shape="circle")

            # Krawędzie z wymuszonym kolorem (zielony dla aktywnych)
            for u, edges in menadzer.siec.sasiedztwo.items():
                for e in edges:
                    if e.przepustowosc > 0:
                        is_active = e.przeplyw > 0
                        
                        # Definicja tekstu w dymku
                        if u == "START":
                            txt = "Status: Zatrudniony" if is_active else "Status: Wolny"
                        elif e.cel == "KONIEC":
                            txt = f"Wydobycie z tego złoża: {e.przeplyw} / {e.przepustowosc}"
                        else:
                            txt = f"Dystans: {e.koszt} km\nStatus: {'✅ Wybrano' if is_active else '❌ Nie wybrano'}"
                        
                        net.add_edge(u, e.cel, 
                                     title=txt, 
                                     color="#2ca02c" if is_active else "#e0e0e0", 
                                     width=3.5 if is_active else 1,
                                     opacity=1.0 if is_active else 0.4)

            # --- GENEROWANIE HTML Z WŁASNYM PRZYCISKIEM FULLSCREEN ---
            html_string = net.generate_html()

            # Wstrzykujemy przycisk i skrypt JS do obsługi prawdziwego fullscreena przed końcem tagu body
            fullscreen_script = """
            <div style="position: absolute; top: 10px; right: 10px; z-index: 1000;">
                <button onclick="toggleFullScreen();" style="padding: 10px 15px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; font-family: sans-serif; font-size: 14px;">
                    🖥️ Pełny Ekran
                </button>
            </div>
            <script>
                function toggleFullScreen() {
                    var elem = document.body;
                    if (!document.fullscreenElement) {
                        elem.requestFullscreen().catch(err => {
                            alert("Błąd przy wchodzeniu w pełny ekran: " + err.message);
                        });
                    } else {
                        document.exitFullscreen();
                    }
                }
            </script>
            <style>
                /* Wymuszenie, aby kontener zajmował 100% miejsca */
                #mynetwork {
                    height: 100vh !important;
                    width: 100% !important;
                }
                body {
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                }
            </style>
            """
            
            # Wstrzykujemy skrypt i style
            html_string = html_string.replace('</body>', fullscreen_script + '</body>')
            
            # Zmieniamy parametry w samym HTML-u pyvis dla pewności
            html_string = html_string.replace('height: 700px;', 'height: 100vh !important;')
            
            # Wyświetlenie z wysokością 850px w Streamlit (ale wewnątrz będzie się rozciągać)
            st.iframe(html_string, height=850)

# ==========================================
# MODUŁ II: PATROL KSIĘCIA (GEOMETRIA)
# ==========================================
elif modul == "🐎 Moduł II: Patrol Księcia (Otoczka wypukła)":
    st.header("🐎 Konfiguracja i Trasa Patrolu Księcia")
    
    # 1. Wyliczamy przepływy (MCMF), aby wiedzieć, które kopalnie pracują
    if len(st.session_state.krasnale_m1) >= 7 and len(st.session_state.zloza_m1) > 0:
        menadzer_m2 = MenadzerPrzydzialu(st.session_state.krasnale_m1, st.session_state.zloza_m1, st.session_state.tabela_odl)
        menadzer_m2.buduj_siec()
        menadzer_m2.oblicz_mcmf()
        aktywne_zloza = menadzer_m2.daj_aktywne_zloza()
    else:
        aktywne_zloza = []

    col_punkty, col_mapa = st.columns([1, 1.5])

    with col_punkty:
        st.subheader("📍 Współrzędne Kopalń Królestwa")
        st.info("Dodawanie kopalni odbywa się w Module 1. Tutaj ustalasz ich dokładną fizyczną lokację na mapie.")

        if len(aktywne_zloza) == 0:
            st.warning("Brak aktywnych kopalń.")
            
        else:
            for z in aktywne_zloza:
                c1, c2 = st.columns([1, 1])
                with c1:
                    z.x = st.number_input(
                        f"X [{z.nazwa} - {z.id_zloza}]", 
                        min_value=-50.0, 
                        max_value=50.0, 
                        value=float(z.x), 
                        key=f"x_m2_{z.id_zloza}_{st.session_state.form_key}", 
                        step=0.1
                    )
                with c2:
                    z.y = st.number_input(
                        f"Y [{z.nazwa} - {z.id_zloza}]", 
                        min_value=-50.0, 
                        max_value=50.0, 
                        value=float(z.y), 
                        key=f"y_m2_{z.id_zloza}_{st.session_state.form_key}", 
                        step=0.1
                    )

    with col_mapa:

        # 2. Pobieramy współrzędne TYLKO dla aktywnych złóż
        aktualne_punkty = [(z.x, z.y) for z in aktywne_zloza]
        mapa_nazw = {(z.x, z.y): z.id_zloza for z in aktywne_zloza}
        
        if len(aktualne_punkty) == 0:
            st.warning("Królestwo nie posiada obecnie żadnych AKTYWNYCH złóż (z przypisanymi pracownikami i przepływem > 0). Wróć do Modułu I i zadbaj o przydział!")
        else:
            # Rozróżnienie logiki na obronę stacjonarną (1 złoże) i patrol (2+ złóż)
            if len(aktualne_punkty) == 1:
                obwod = 0.0
                st.info("📍 Wykryto 1 aktywną kopalnię. Książę obejmuje obronę stacjonarną (Brak trasy patrolu).")
            else:
                otoczka = get_convex_hull(aktualne_punkty)
                obwod = calculate_perimeter(otoczka)
            
            st.metric(label="Długość muru / obwód patrolu", value=f"{obwod:.2f} metrów")
            
            # --- GENEROWANIE WYKRESU ---
            fig, ax = plt.subplots(figsize=(6, 6))
            px, py = zip(*aktualne_punkty)
            
            # Rysujemy punkty kopalni (zadziała zawsze, nawet dla 1 punktu)
            ax.scatter(px, py, color='#a8cf45', s=120, zorder=3, label="Kopalnie")
            
            # Podpisy kopalni
            for punkt in aktualne_punkty:
                id_zloza = mapa_nazw.get(punkt, "?")
                ax.annotate(id_zloza, punkt, textcoords="offset points", xytext=(0,8), ha='center', weight='bold', color='black')
            
            # Rysowanie trasy (TYLKO gdy mamy min. 2 punkty)
            if len(aktualne_punkty) >= 2 and len(otoczka) >= 2:
                ox, oy = zip(*(otoczka + [otoczka[0]]))
                ax.plot(ox, oy, 'r--', linewidth=2.5, zorder=2, label="Trasa Księcia")
                # --- WIZUALNY DOWÓD: Zaznaczamy tylko prawdziwe wierzchołki otoczki! ---
                ax.scatter(ox, oy, color='red', edgecolors='black', s=150, zorder=4, marker='*', label="Punkty Kontrolne")

            ax.grid(True, linestyle='--', alpha=0.5)
            ax.set_aspect('equal', adjustable='datalim')
            
            # Pokazujemy legendę i renderujemy wykres
            ax.legend()
            st.pyplot(fig)

# ==========================================
# MODUŁ III: OBRONA GRANIC (STRUKTURY)
# ==========================================
elif modul == "🛡️ Moduł III: Obrona Granic (Wybór dekametrowca)":
    st.header("🛡️ Interaktywny System Defensywny Granic")
    
    col_ustawienia, col_wykres = st.columns([1, 1.5])

    with col_ustawienia:
        st.subheader("👥 Edycja Parametrów Bojowych Krasnali")
        st.info("Zarządzasz bezpośrednio krasnalami zatrudnionymi w Module I.")
        
        if len(st.session_state.krasnale_m1) < 7:
            st.error(f"❌ W królestwie pracuje aktualnie {len(st.session_state.krasnale_m1)} krasnali. Zgodnie z prawem, potrzebujemy minimum 7 żołnierzy do obstawienia murów. Dodaj poddanych w Module I.")
        
        for k in st.session_state.krasnale_m1:
            c1, c2 = st.columns([2, 1])
            with c1:
                k.imie = st.text_input(f"Imię ({k.id_krasnala})", value=k.imie, key=f"name_m3_{k.id_krasnala}_{st.session_state.form_key}")
            with c2:
                k.glosnosc = st.number_input(f"dB", min_value=0, max_value=150, value=k.glosnosc, key=f"vol_m3_{k.id_krasnala}_{st.session_state.form_key}")
            
            if int(k.glosnosc) == 0:
                st.info(f"🤐 {k.imie} jest niemową (0 dB).")
            elif int(k.glosnosc) == 1:
                st.caption(f"🐭 {k.imie} postanowił tylko szeptać (1 dB). Trzeba nadstawić ucha!")

    glosnosci = [k.glosnosc for k in st.session_state.krasnale_m1]
    imiona = [k.imie for k in st.session_state.krasnale_m1]
    dane_granicy = list(zip(glosnosci, imiona))
    
    if dane_granicy and len(dane_granicy) >= 7:
        drzewo = DrzewoPrzedzialowe(dane_granicy)

        with col_wykres:
            st.subheader("🏹 Symulator Odparcia Ataku")
            
            st.write("Wybierz obszar uderzenia wroga za pomocą suwaka przedziału:")
            obszar_ataku = st.slider(
                "Zakres metrów granicy (Każdy metr to jeden krasnal):",
                min_value=1,
                max_value=max(1, len(glosnosci)),
                value=(1, max(1, len(glosnosci))),
                key=f"slider_obszar_{st.session_state.form_key}"
            )
            poczatek, koniec = obszar_ataku
            idx_poczatek = poczatek - 1
            idx_koniec = koniec - 1
            st.session_state.atak_start = idx_poczatek
            st.session_state.atak_koniec = idx_koniec

            najglosniejszy = drzewo.znajdz_najglosniejszego(idx_poczatek, idx_koniec)

            st.error(f"🚨 ALERT! Wróg uderzył w odcinek od {poczatek} do {koniec} metra granicy!")
            if najglosniejszy[0] != float('-inf'):
                
                if najglosniejszy[0] == 0:
                    st.warning(f"🤫 Dowódca {najglosniejszy[1]} to niemowa! Rozkaz obrony w absolutnej ciszy (0 dB)... To raczej nie zadziała.")
                elif najglosniejszy[0] == 1:
                    st.warning(f"🐭 Najgłośniejszy na tym odcinku jest {najglosniejszy[1]}... ale on tylko szepcze (1 dB). Krasnale muszą czytać mu z ruchu warg!")
                else:
                    st.success(f"📢 Rozkaz obrony wydaje: **{najglosniejszy[1]}** (Głośność okrzyku: {najglosniejszy[0]} dB)")
                    st.info(f"⚔️ Głos dowódcy niesie przesłanie: „Strzały na cięciwy – naciągnąć cięciwy – strzał!”")
            
            ids_k = [k.id_krasnala for k in st.session_state.krasnale_m1]
            df_wykres = pd.DataFrame({
                'Metr Granicy': list(range(1, len(glosnosci) + 1)),
                'Głośność (dB)': glosnosci,
                'Imię': imiona,
                'ID': ids_k
            })

            # 2. Logika przypisywania kategorii (kolorów) do słupków
            def przypisz_kolor(row):
                if row['Głośność (dB)'] == najglosniejszy[0] and row['Imię'] == najglosniejszy[1]:
                    return 'Dowódca Sektora'
                elif poczatek <= row['Metr Granicy'] <= koniec:
                    return 'Strefa Ataku'
                else:
                    return 'Pozostałe Jednostki'

            df_wykres['Status'] = df_wykres.apply(przypisz_kolor, axis=1)

            kolory_mapa = {
                'Dowódca Sektora': '#ff4b4b',
                'Strefa Ataku': '#ffaa00',
                'Pozostałe Jednostki': '#1f77b4'
            }

            # 3. Tworzymy wykres
            fig_plotly = px.bar(
                df_wykres,
                x='Metr Granicy',
                y='Głośność (dB)',
                color='Status',
                color_discrete_map=kolory_mapa,
                title="Wizualizacja Rozstawienia i Głośności na Murach",
                hover_data={
                    'Metr Granicy': True,
                    'Imię': True,
                    'Głośność (dB)': ':.0f',
                    'ID': True,
                    'Status': False
                }
            )

            # 4. Stylizujemy wykres, aby był czytelny bez względu na ilość krasnali
            fig_plotly.update_layout(
                xaxis_title="Pozycja na metrach granicy",
                yaxis_title="Głośność okrzyku (dB)",
                legend_title_text='Legenda Taktyczna',
                height=450,
                xaxis=dict(
                    tickmode='linear', 
                    dtick=5 if len(glosnosci) > 30 else 1 # Skalowanie osi X przy dużych liczbach
                )
            )

            # 5. Rysujemy na ekranie
            st.plotly_chart(fig_plotly, width='stretch')

# ==========================================
# MODUŁ IV: KRÓLEWSKIE ARCHIWUM (HUFFMAN I KMP)
# ==========================================
elif modul == "📜 Moduł IV: Królewskie Archiwum (KMP i Huffman)":
    st.header("📜 Królewskie Archiwum i Kompresja Wiedzy")
    st.write("System bezpiecznej archiwizacji danych królestwa przy użyciu kryptografii Huffmana.")

    # Zapewnienie, że obiekt kompresora istnieje w sesji
    if 'kompresor' not in st.session_state:
        st.session_state.kompresor = KompresorKsiag() 

    # --- FUNKCJA GENERUJĄCA POTĘŻNY RAPORT Z MODUŁU I ---
    def generuj_wielki_raport():
        if not st.session_state.krasnale_m1 and not st.session_state.zloza_m1:
            return "Kronika Królestwa jest pusta. Brak wystarczających danych do przeprowadzenia integracji modułów."
        
        raport = []
        raport.append("=== WIELKA KRONIKA KRÓLESTWA KRASNALI ===")
        raport.append("Dokument ściśle tajny. Wygenerowany przez Zintegrowany System Dowodzenia.\n")
        
        # ---------------------------------------------------------
        # ANALIZA Z MODUŁU I (PRZYDZIAŁ PRACY I LOGISTYKA)
        # ---------------------------------------------------------
        raport.append("--- SEKCJA I: RAPORT GOSPODARCZY I LOGISTYKA (Algorytm MCMF) ---")
        menadzer = MenadzerPrzydzialu(st.session_state.krasnale_m1, st.session_state.zloza_m1, st.session_state.tabela_odl)
        menadzer.buduj_siec()
        max_przeplyw, min_koszt = menadzer.oblicz_mcmf()
        raport.append(f"Podsumowanie globalne: Do pracy przydzielono {max_przeplyw} krasnali. Całkowity koszt logistyczny wynosi {min_koszt} kilometrów.")
        
        # Wyciąganie szczegółów z grafu
        przydzialy = {}
        obsada_zloz = {z.id_zloza: [] for z in st.session_state.zloza_m1}

        for u, edges in menadzer.siec.sasiedztwo.items():
            if str(u).startswith("K"): # Szukamy węzłów krasnali
                for e in edges:
                    # Jeśli krawędź prowadzi do złoża i ma przepływ
                    if e.cel.startswith("Z") and e.przeplyw > 0:
                        przydzialy[u] = (e.cel, e.koszt)
                        imie_k = next((k.imie for k in st.session_state.krasnale_m1 if k.id_krasnala == u), u)
                        obsada_zloz[e.cel].append(f"{imie_k} ({u})")

        raport.append("\nSzczegółowy wykaz zatrudnienia:")
        for k in st.session_state.krasnale_m1:
            if k.id_krasnala in przydzialy:
                zloze_id, dystans = przydzialy[k.id_krasnala]
                nazwa_zloza = next((z.nazwa for z in st.session_state.zloza_m1 if z.id_zloza == zloze_id), zloze_id)
                raport.append(f" - Krasnal {k.imie} ({k.id_krasnala}) został pomyślnie przydzielony do kopalni {nazwa_zloza}. Dystans dojazdu: {dystans} km.")
            else:
                if not k.umiejetnosci:
                    # Brak jakichkolwiek umiejętności w obiekcie krasnala
                    raport.append(f"-HR ALERT: Krasnal {k.imie} ({k.id_krasnala}) pozostaje BEZROBOTNY. Przyczyna: Brak jakichkolwiek kwalifikacji zawodowych (leń).")
                else:
                    # Krasnal ma umiejętności, ale system go odrzucił. Wyciągamy ładne nazwy kopalń, w których ma fach.
                    nazwy_fachow = [next((z.nazwa for z in st.session_state.zloza_m1 if z.id_zloza == f), f) for f in k.umiejetnosci]
                    fachy_str = ", ".join(nazwy_fachow)
                    raport.append(f"-LOGISTYKA ALERT: Krasnal {k.imie} ({k.id_krasnala}) jest BEZROBOTNY. Przyczyna: Brak wolnych miejsc w kopalniach ({fachy_str}) lub dojazd był nieopłacalny.")

        raport.append("\nObsada kopalń:")
        
        # Dwie osobne listy dla dwóch różnych przyczyn pustej kopalni
        zloza_bez_przydzialu = []
        zloza_wyczerpane = []
        
        for z in st.session_state.zloza_m1:
            pracownicy = obsada_zloz.get(z.id_zloza, [])
            if pracownicy:
                pracownicy_str = ", ".join(pracownicy)
                raport.append(f"  - Kopalnia {z.nazwa} ({z.id_zloza}) [Maks. wydajność: {z.wydajnosc}] -> Pracuje tu: {pracownicy_str}")
            else:
                # Rozróżniamy powód braku pracowników na podstawie wydajności złoża
                if z.wydajnosc == 0:
                    zloza_wyczerpane.append(f"{z.nazwa} ({z.id_zloza})")
                else:
                    zloza_bez_przydzialu.append(f"{z.nazwa} ({z.id_zloza})")

        # --- INTELIGENTNE ALERTY O PUSTYCH ZŁOŻACH ---
        # 1. Alarm logistyczny (kopalnia sprawna, ale nikt w niej nie pracuje)
        if zloza_bez_przydzialu:
            raport.append("\nWARNING: Alarm gospodarczy! Wykryto sprawne złoża bez obsady (Zaniedbany potencjał wydobywczy):")
            for p_zloze in zloza_bez_przydzialu:
                raport.append(f"  ! Złoże {p_zloze} jest OPUSZCZONE. Posiada przepustowość, ale żaden krasnal nie podjął tam pracy!")
        else:
            raport.append("\nStan operacyjny stabilny: Wszystkie sprawne kopalnie w królestwie posiadają przynajmniej minimalną obsadę.")

        # 2. Informacja administracyjna (kopalnia ma wydajność 0)
        if zloza_wyczerpane:
            raport.append("\nINFO: Raport o kopalniach zamkniętych/wyczerpanych:")
            for w_zloze in zloza_wyczerpane:
                raport.append(f"  - Złoże {w_zloze} stoi puste, ponieważ jego zasoby są wyczerpane lub wydajność ustawiono na 0.")
        # ---------------------------------------------------------
        # ANALIZA Z MODUŁU II (BEZPIECZEŃSTWO I GRANICE)
        # ---------------------------------------------------------
        raport.append("\n--- SEKCJA II: RAPORT KARTOGRAFICZNY I PATROL KSIĘCIA (Algorytm Grahama) ---")
        aktywne_zloza = menadzer.daj_aktywne_zloza()
        aktualne_punkty = [(z.x, z.y) for z in aktywne_zloza]
        mapa_nazw = {(z.x, z.y): f"{z.nazwa}({z.id_zloza})" for z in aktywne_zloza}

        if len(aktualne_punkty) >= 3:
            otoczka = get_convex_hull(aktualne_punkty)
            obwod = calculate_perimeter(otoczka)
            raport.append(f"Wokół aktywnych kopalń z powodzeniem wytyczono bezpieczną strefę militarną (Otoczka Wypukła).")
            raport.append(f"Całkowita długość trasy patrolu dla Księcia wynosi {obwod:.2f} kilometrów.")
            raport.append("Trasa patrolu wyznacza wierzchołki przez następujące strategiczne kopalnie:")
            for pkt in otoczka:
                raport.append(f" -> Punkt kontrolny: {mapa_nazw.get(pkt, 'Nieznany')} na współrzędnych [X: {pkt[0]}, Y: {pkt[1]}]")
        elif len(aktualne_punkty) == 2:
            # Liniowa trasa patrolowa (tam i z powrotem)
            pkt1, pkt2 = aktualne_punkty[0], aktualne_punkty[1]
            # Matematyczne obliczenie dystansu (Twierdzenie Pitagorasa)
            dystans = ((pkt1[0] - pkt2[0])**2 + (pkt1[1] - pkt2[1])**2) ** 0.5
            obwod = 2 * dystans
            raport.append(f"Wykryto dokładnie 2 aktywne kopalnie. Wytyczono liniową trasę patrolu (odcinek z powrotem).")
            raport.append(f"Całkowita długość trasy (tam i z powrotem) wynosi {obwod:.2f} kilometrów.")
            raport.append("Książę będzie nieustannie kursował pomiędzy punktami:")
            raport.append(f" <-> Punkt A: {mapa_nazw.get(pkt1, 'Nieznany')} [X: {pkt1[0]}, Y: {pkt1[1]}]")
            raport.append(f" <-> Punkt B: {mapa_nazw.get(pkt2, 'Nieznany')} [X: {pkt2[0]}, Y: {pkt2[1]}]")
            
        elif len(aktualne_punkty) == 1:
            # Punktowa obrona stacjonarna
            pkt = aktualne_punkty[0]
            raport.append(f"Wykryto tylko 1 aktywną kopalnię w całym królestwie: {mapa_nazw.get(pkt, 'Nieznany')}.")
            raport.append("Książę obejmuje obronę stacjonarną. Brak wytyczonej trasy patrolu (0.00 km).")
            
        else:
            # Królestwo nie pracuje
            raport.append("Ostrzeżenie: Brak jakichkolwiek aktywnych kopalń z pracującymi krasnalami. Książę pozostaje w zamku.")

        # ---------------------------------------------------------
        # ANALIZA Z MODUŁU III (OBRONA GRANIC I DOWODZENIE)
        # ---------------------------------------------------------
        raport.append("\n--- SEKCJA III: RAPORT OBRONNY MURU (Drzewo Przedziałowe) ---")
        glosnosci = [k.glosnosc for k in st.session_state.krasnale_m1]
        imiona = [k.imie for k in st.session_state.krasnale_m1]
        dane_granicy = list(zip(glosnosci, imiona))
        
        if len(dane_granicy) >= 7:
            drzewo = DrzewoPrzedzialowe(dane_granicy)
            n = len(dane_granicy)
            
            # Dowódca całego muru
            najglosniejszy_ogolem = drzewo.znajdz_najglosniejszego(0, n - 1)
            raport.append(f"Stan gotowości: {n} dekametrowców na pozycjach.")
            raport.append(f"Głównodowodzącym całej linii obrony zostaje {najglosniejszy_ogolem[1]} z potężnym okrzykiem {najglosniejszy_ogolem[0]} decybeli.")
            
            if 'atak_start' in st.session_state and 'atak_koniec' in st.session_state:
                pocz = st.session_state.atak_start
                kon = st.session_state.atak_koniec
                
                # Zabezpieczenie na wypadek dodania/usunięcia krasnali w międzyczasie
                pocz_bezp = max(0, min(pocz, n - 1))
                kon_bezp = max(0, min(kon, n - 1))
                
                oficer = drzewo.znajdz_najglosniejszego(pocz_bezp, kon_bezp)
                raport.append(f" POTWIERDZONY INCYDENT: Zmasowany atak jabłkami na odcinek granicy od dekametrowca nr {pocz_bezp + 1} do nr {kon_bezp + 1}.")                
                # Reakcja na szczególne wartości głośności (zgodnie z Modułem III)
                if oficer[0] == 0:
                    raport.append(f"KATASTROFA: Rozkaz próbował wydać niemowa {oficer[1]} (0 dB). Próba obrony nieudana, jabłka zasypały mur.")
                elif oficer[0] == 1:
                    raport.append(f"OSTRZEŻENIE: Rozkaz wyszeptał {oficer[1]} (1 dB). Komunikacja obronna poważnie utrudniona, krasnale czytały z ruchu warg.")
                else:
                    raport.append(f"Rozkaz 'strzały na cięciwy – naciągnąć cięciwy – strzał!' pewnie wydał: {oficer[1]} ({oficer[0]} dB).")
                    raport.append("Salwa skuteczna. Atak odparto.")
            else:
                raport.append("Brak odnotowanych ataków na konkretne odcinki muru w bieżącej sesji operacyjnej.")
                raport.append("(Przejdź do Modułu III, przesuń suwak ataku, a incydent zostanie tu zarejestrowany).")
                
        else:
            raport.append("Ostrzeżenie: Brak wystarczającej liczby dekametrowców na murze (wymagane minimum 7).")

        raport.append("\n=== KONIEC RAPORTU ===")
        return "\n".join(raport)

    def generuj_i_zakoduj_w_pamieci():
        surowy_tekst = generuj_wielki_raport()
        if surowy_tekst == "Kronika Królestwa jest pusta. Brak wystarczających danych do przeprowadzenia integracji modułów.":
            st.session_state.huff_binarny = ""
            st.session_state.huff_korzen = None
            st.session_state.huff_oryginalny_rozmiar = 0
        else:
            # Kompresujemy tekst zanim ktokolwiek go zobaczy!
            skompresowany, korzen = st.session_state.kompresor.kompresuj_tekst(surowy_tekst)
            st.session_state.huff_binarny = skompresowany
            st.session_state.huff_korzen = korzen
            st.session_state.huff_oryginalny_rozmiar = len(surowy_tekst) * 8
        # Resetujemy poprzednio zdekodowany raport przy nowym generowaniu
        if 'huff_zdekodowany' in st.session_state:
            st.session_state.huff_zdekodowany = ""

    # --- CALLBACK: DEKOMPRESJA NA ŻĄDANIE ---
    def odkoduj_raport():
        if st.session_state.get('huff_binarny') and st.session_state.get('huff_korzen'):
            # Wywołujemy funkcję dekodującą
            st.session_state.huff_zdekodowany = st.session_state.kompresor.dekompresuj_tekst(
                st.session_state.huff_binarny, st.session_state.huff_korzen
            )

    # Przycisk startowy procesu
    st.button("🔒 Uruchom integrację i zaszyfruj raport w Skarbcu", width='stretch', on_click=generuj_i_zakoduj_w_pamieci)

    # Sprawdzamy czy mamy dane w skarbcu
    if st.session_state.get('huff_binarny'):
        
        col_lewa, col_prawa = st.columns([1, 1.2])
        
        with col_lewa:
            st.subheader("🗜️ Stan Cyfrowego Skarbca")
            rozmiar_bity = len(st.session_state.huff_binarny)
            oryg_bity = st.session_state.huff_oryginalny_rozmiar
            oszczednosc = 100 - ((rozmiar_bity / oryg_bity) * 100) if oryg_bity > 0 else 0
            
            st.success("Raport pomyślnie przechwycony i skompresowany w pamięci RAM!")
            c1, c2 = st.columns(2)
            c1.metric("Rozmiar surowy (bity)", f"{oryg_bity}")
            c2.metric("Rozmiar w Skarbcu (bity)", f"{rozmiar_bity}", delta=f"-{oszczednosc:.1f}%", delta_color="inverse")
            
            st.caption("🔒 **Zaszyfrowany ciąg binarny gotowy do pobrania:**")
            st.code(st.session_state.huff_binarny, language="text")
            
            # PRZYCISK POBIERANIA ZAKODOWANEGO RAPORTU (CONCEPTUAL COMPRESSED FILE)
            st.download_button(
                label="💾 Pobierz zakodowany plik binarny (.txt)",
                data=st.session_state.huff_binarny,
                file_name="zakodowany_raport_huffmana.txt",
                mime="text/plain",
                width='stretch'
            )
            
            st.markdown("---")
            # Przycisk do zdekodowania i odczytania raportu
            st.button("🔓 Odkoduj i odczytaj księgę raportów", width='stretch', on_click=odkoduj_raport)

        with col_prawa:
            st.subheader("📖 Ekran Odkodowanej Wiedzy")
            
            @st.dialog("📖 Pełnoekranowy Widok Kroniki Królestwa", width="large")
            def otworz_pelny_ekran(tekst):
                # Parametr label_visibility="collapsed" ukrywa napis nad polem dla lepszego efektu
                st.text_area("Treść:", value=tekst, height=750, label_visibility="collapsed")
            # Wyświetlamy raport tylko, jeśli został jawnie odkodowany przyciskiem
            zdekodowany_tekst = st.session_state.get('huff_zdekodowany', "")
            
            if zdekodowany_tekst:
                if st.button("🖵 Otwórz raport w powiększonym oknie", width='stretch'):
                    otworz_pelny_ekran(zdekodowany_tekst)

                st.text_area("Odczytana zawartość kroniki królestwa:", value=zdekodowany_tekst, height=350, key="widok_kroniki")
                
                # SEKCJA WYSZUKIWANIA KMP - działa tylko na odkodowanym tekście!
                st.markdown("---")
                st.write("**🔍 Szybkie przeszukiwanie odkodowanej księgi (KMP):**")
                szukane_slowo = st.text_input("Wpisz szukaną frazę:", "")
                
                if st.button("🔎 Szukaj frazy", width='stretch'):
                    if not szukane_slowo:
                        st.warning("Wpisz szukaną frazę.")
                    else:
                        pozycje = st.session_state.kompresor.szukaj_kmp(zdekodowany_tekst.lower(), szukane_slowo.lower())
                        if pozycje:
                            st.success(f"Algorytm KMP odnalazł {len(pozycje)} wystąpień!")
                            for poz in pozycje[:3]: # pokazujemy maksymalnie 3 wyniki
                                # 1. Szukamy najbliższego znaku nowej linii w lewo (początek obecnej linii)
                                poczatek_linii = zdekodowany_tekst.rfind('\n', 0, poz)
                                poczatek_linii = poczatek_linii + 1 if poczatek_linii != -1 else 0
                                # 2. Szukamy najbliższego znaku nowej linii w prawo (koniec obecnej linii)
                                koniec_linii = zdekodowany_tekst.find('\n', poz)
                                koniec_linii = koniec_linii if koniec_linii != -1 else len(zdekodowany_tekst)
                                # 3. Ustalamy bezpieczne ramy wycinka (np. max 40 znaków), ale NIE przekraczamy granic linii!
                                start = max(poczatek_linii, poz - 40)
                                koniec = min(koniec_linii, poz + len(szukane_slowo) + 40)
                            
                                fragment = zdekodowany_tekst[start:koniec]
                                # 4. Dodajemy estetyczne trzykropki TYLKO wtedy, gdy linia jest ucięta
                                prefiks = "..." if start > poczatek_linii else ""
                                sufiks = "..." if koniec < koniec_linii else ""
                                # 5. Pogrubiamy szukane słowo
                                fragment_bold = fragment.replace(zdekodowany_tekst[poz:poz+len(szukane_slowo)], f"**{zdekodowany_tekst[poz:poz+len(szukane_slowo)]}**")
                                numer_linii = zdekodowany_tekst.count('\n', 0, poz) + 1
                                
                                st.info(f"📍 Linia {numer_linii}: \"{prefiks}{fragment_bold}{sufiks}\"")
                            
                            if len(pozycje) > 3:
                                st.caption(f"...oraz {len(pozycje) - 3} kolejnych lokalizacji.")
                        else:
                            st.error(f"Fraza '{szukane_slowo}' nie występuje w tym dokumencie.")
            else:
                st.info("System czeka na autoryzację. Kliknij przycisk po lewej stronie, aby uruchomić dekompresor drzewa Huffmana i odczytać treść raportów.")
                
    elif st.session_state.get('huff_binarny') == "":
        st.warning("Księga jest pusta! Wgraj dane lub wygeneruj zasoby w Module I.")
        
    else:
        # Obsługa błędów KMP dla pustej księgi
        st.info("Skarbiec jest obecnie pusty. Wygeneruj raport za pomocą przycisku na górze.")
        szukane_slowo_puste = st.text_input("Wpisz szukaną frazę:", "", key="pusty_szukaj")
        if st.button("🔎 Szukaj frazy", width='stretch', key="pusty_btn"):
            st.warning("Księga jest pusta!")