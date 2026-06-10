import streamlit as st
import networkx as nx
import random
import json
import streamlit.components.v1 as components
from pyvis.network import Network

# Importy z Twojego projektu
from modele import Krasnal, Zloze
from przydzial_pracy import MenadzerPrzydzialu
from otoczka import get_convex_hull, calculate_perimeter
from struktury import DrzewoPrzedzialowe
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
     "🛡️ Moduł III: Obrona Granic (Wybór dekametrowca)"],
    key="wybrany_modul"
)
st.sidebar.markdown("---")

st.sidebar.header("📁 Źródło Danych")
wgrany_plik = st.sidebar.file_uploader("Wgraj własny plik JSON", type=["json"])

if st.sidebar.button("Załaduj plik JSON", use_container_width=True):
    if wgrany_plik is not None:
        dane_z_pliku = json.load(wgrany_plik)
        zaladuj_dane_z_pliku(dane_z_pliku)
        st.rerun() 
    else:
        st.sidebar.error("Najpierw wybierz plik!")

st.sidebar.markdown("lub")

if st.sidebar.button("🎲 Wygeneruj losowe dane", use_container_width=True):
    generuj_losowe_dane()
    st.rerun()
    
if len(st.session_state.krasnale_m1) > 0 or len(st.session_state.zloza_m1) > 0:
    if st.sidebar.button("🗑️ Wyczyść wszystkie dane", use_container_width=True):
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
                nowe_id = f"Z{len(st.session_state.zloza_m1) + 1}"
                while any(z.id_zloza == nowe_id for z in st.session_state.zloza_m1):
                    nowe_id = f"Z{random.randint(10, 999)}"
                st.session_state.zloza_m1.append(Zloze(nowe_id, nowe_z_nazwa, nowe_z_wydajnosc, nowe_z_x, nowe_z_y))
                st.success(f"Dodano złoże {nowe_z_nazwa}!")
                st.rerun()
        
        if len(st.session_state.zloza_m1) > 0:
            zloza_kopia = list(st.session_state.zloza_m1)
            for idx, z in enumerate(zloza_kopia):
                c_name, c_input, c_del = st.columns([2, 2, 1])
                with c_name:
                    st.write(f"**{z.nazwa}({z.id_zloza})**")
                with c_input:
                    z.wydajnosc = st.number_input("Wydajność:", min_value=0, max_value=10, value=int(z.wydajnosc), key=f"wyd_{z.id_zloza}_{st.session_state.form_key}", label_visibility="collapsed")
                with c_del:
                    if st.button("🗑️", key=f"del_zloze_{z.id_zloza}"):
                        st.session_state.zloza_m1.pop(idx)
                        for k in st.session_state.krasnale_m1:
                            if z.id_zloza in k.umiejetnosci:
                                k.umiejetnosci.remove(z.id_zloza)
                                if (k.id_krasnala, z.id_zloza) in st.session_state.tabela_odl:
                                    del st.session_state.tabela_odl[(k.id_krasnala, z.id_zloza)]
                        st.rerun()
        
        st.write("**--- Zarządzanie Krasnalami ---**")
        with st.expander("➕ Dodaj Nowego Krasnala", expanded=(len(st.session_state.krasnale_m1) == 0)):
            nowe_imie = st.text_input("Imię nowego krasnala:", key=f"nowe_imie_{st.session_state.form_key}")
            nowa_glosnosc = st.number_input("Głośność (dB):", min_value=0, max_value=150, value=50, key=f"nowa_gl_k_{st.session_state.form_key}")
            wszystkie_zloza_ids = [z.id_zloza for z in st.session_state.zloza_m1]
            nowe_fachy = st.multiselect("Fachy nowego krasnala (Złoża z listy powyżej):", wszystkie_zloza_ids, key=f"nowe_fachy_{st.session_state.form_key}")
            
            if st.button("Dodaj do królestwa"):
                new_id = f"K{len(st.session_state.krasnale_m1) + 1}"
                while any(k.id_krasnala == new_id for k in st.session_state.krasnale_m1):
                    new_id = f"K{random.randint(10, 999)}"
                
                st.session_state.krasnale_m1.append(Krasnal(new_id, nowe_imie, nowe_fachy, nowa_glosnosc))
                
                for fach in nowe_fachy:
                     st.session_state.tabela_odl[(new_id, fach)] = random.randint(1, 50)
                     
                st.success(f"Dodano krasnala {nowe_imie}!")
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
            
            if st.button("Zatwierdź zmiany fachu"):
                for fach in nowe_umiejetnosci:
                    if (wybrany_k.id_krasnala, fach) not in st.session_state.tabela_odl:
                        st.session_state.tabela_odl[(wybrany_k.id_krasnala, fach)] = random.randint(1, 50)
                wybrany_k.umiejetnosci = nowe_umiejetnosci
                st.success(f"Zaktualizowano fachy dla {wybrany_k.imie}!")
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
            # Zwiększamy height ramki
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
                            label=k.id_krasnala, # Emotikona zamiast tekstu
                            title=f"👤 Imię: {k.imie}\n🔊 Głośność: {k.glosnosc} dB", 
                            color="#82c3df",
                            x=300, y=y_pos,
                            size=40,  
                            shape="circle")
            
            len_z = len(st.session_state.zloza_m1)
            for i, z in enumerate(st.session_state.zloza_m1):
                y_pos = (i - len_z / 2) * 120 # Większy odstęp pionowy między złożami
                net.add_node(z.id_zloza, 
                            label=z.id_zloza, # Emotikona zamiast tekstu
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
    
    col_punkty, col_mapa = st.columns([1, 1.5])

    with col_punkty:
        st.subheader("📍 Współrzędne Kopalń Królestwa")
        st.info("Dodawanie kopalni odbywa się w Module 1. Tutaj ustalasz ich dokładną fizyczną lokację na mapie.")

        if len(st.session_state.zloza_m1) == 0:
            st.write("Brak kopalń do edycji.")
            
        for idx, z in enumerate(st.session_state.zloza_m1):
            c1, c2 = st.columns([1, 1])
            with c1:
                z.x = st.number_input(f"X [{z.nazwa} - {z.id_zloza}]", min_value=-50.0, max_value=50.0, value=float(z.x), key=f"x_m2_{z.id_zloza}_{st.session_state.form_key}", step=0.1)
            with c2:
                z.y = st.number_input(f"Y [{z.nazwa} - {z.id_zloza}]", min_value=-50.0, max_value=50.0, value=float(z.y), key=f"y_m2_{z.id_zloza}_{st.session_state.form_key}", step=0.1)

    with col_mapa:
        # 1. Wyliczamy przepływy (MCMF), aby wiedzieć, które kopalnie pracują
        if len(st.session_state.krasnale_m1) >= 7 and len(st.session_state.zloza_m1) > 0:
            menadzer_m2 = MenadzerPrzydzialu(st.session_state.krasnale_m1, st.session_state.zloza_m1, st.session_state.tabela_odl)
            menadzer_m2.buduj_siec()
            menadzer_m2.oblicz_mcmf()
            aktywne_zloza = menadzer_m2.daj_aktywne_zloza() # Używamy Twojej funkcji!
        else:
            aktywne_zloza = []

        # 2. Pobieramy współrzędne TYLKO dla aktywnych złóż
        aktualne_punkty = [(z.x, z.y) for z in aktywne_zloza]
        mapa_nazw = {(z.x, z.y): z.id_zloza for z in aktywne_zloza}

        # 3. Zmienione ostrzeżenie - wymaga minimum 2 AKTYWNYCH złóż
        if len(aktualne_punkty) < 2:
            st.warning("Królestwo musi posiadać co najmniej 2 AKTYWNE złoża (z przypisanymi pracownikami i przepływem > 0), aby wyznaczyć trasę patrolu. Wróć do Modułu I i zadbaj o przydział!")
        else:
            otoczka = get_convex_hull(aktualne_punkty)
            obwod = calculate_perimeter(otoczka)
            
            st.metric(label="Długość muru / obwód patrolu", value=f"{obwod:.2f} metrów")
            
            fig, ax = plt.subplots(figsize=(6, 6))
            
            px, py = zip(*aktualne_punkty)
            ax.scatter(px, py, color='#a8cf45', s=120, zorder=3, label="Kopalnie")
            
            for punkt in aktualne_punkty:
                id_zloza = mapa_nazw.get(punkt, "?")
                ax.annotate(id_zloza, punkt, textcoords="offset points", xytext=(0,8), ha='center', weight='bold', color='black')
            
            if len(otoczka) >= 2:
                ox, oy = zip(*(otoczka + [otoczka[0]]))
                ax.plot(ox, oy, 'r--', linewidth=2.5, zorder=2, label="Trasa Księcia")

            ax.grid(True, linestyle='--', alpha=0.5)
            ax.set_aspect('equal', adjustable='datalim')
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
                min_value=0,
                max_value=max(0, len(glosnosci) - 1),
                value=(0, max(0, len(glosnosci) - 1)),
                key=f"slider_obszar_{st.session_state.form_key}"
            )
            poczatek, koniec = obszar_ataku

            najglosniejszy = drzewo.znajdz_najglosniejszego(poczatek, koniec)

            st.error(f"🚨 ALERT! Wróg uderzył w odcinek od {poczatek} do {koniec} metra granicy!")
            if najglosniejszy[0] != float('-inf'):
                
                if najglosniejszy[0] == 0:
                    st.warning(f"🤫 Dowódca {najglosniejszy[1]} to niemowa! Rozkaz obrony w absolutnej ciszy (0 dB)... To raczej nie zadziała.")
                elif najglosniejszy[0] == 1:
                    st.warning(f"🐭 Najgłośniejszy na tym odcinku jest {najglosniejszy[1]}... ale on tylko szepcze (1 dB). Krasnale muszą czytać mu z ruchu warg!")
                else:
                    st.success(f"📢 Rozkaz obrony wydaje: **{najglosniejszy[1]}** (Głośność okrzyku: {najglosniejszy[0]} dB)")
                    st.info(f"⚔️ Głos dowódcy niesie przesłanie: „Strzały na cięciwy – naciągnąć cięciwy – strzał!”")
            
            fig, ax = plt.subplots(figsize=(10, 5))
            x_coords = range(len(glosnosci))
            
            kolory = []
            for i in x_coords:
                if dane_granicy[i] == najglosniejszy:
                    kolory.append('#ff4b4b')
                elif poczatek <= i <= koniec:
                    kolory.append('#ffaa00')
                else:
                    kolory.append('#1f77b4')

            ax.bar(x_coords, glosnosci, color=kolory, edgecolor='black', linewidth=0.7)
            ax.set_xticks(x_coords)
            ax.set_xticklabels(imiona, rotation=45, ha='right', weight='bold')
            ax.set_ylabel("Głośność okrzyku krasnala (dB)", weight='bold')
            ax.set_xlabel("Rozstawienie jednostek na metrach granicy", weight='bold')
            ax.grid(axis='y', linestyle='--', alpha=0.3)
            
            st.pyplot(fig)