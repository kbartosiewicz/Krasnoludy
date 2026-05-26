import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import random

# Importy z Twojego projektu
from modele import Krasnal, Zloze
from przydzial_pracy import MenadzerPrzydzialu
from otoczka import get_convex_hull, calculate_perimeter
from struktury import DrzewoPrzedzialowe

# Konfiguracja strony Streamlit - szeroki layout i responsywność
st.set_page_config(page_title="Królestwo Krasnali - Panel Dowodzenia", layout="wide")

st.title("🏰 Królewski Panel Sterowania Królestwem Krasnali")
st.write("Profesjonalny system zarządzania królestwem w czasie rzeczywistym.")

# Menu boczne do wyboru modułu
modul = st.sidebar.radio(
    "Wybierz moduł królestwa:",
    ["⚒️ Moduł I: Przydział Pracy (Grafy)", 
     "🐎 Moduł II: Patrol Księcia (Geometria)", 
     "🛡️ Moduł III: Obrona Granic (Struktury)"]
)

# INICJALIZACJA PAMIĘCI SESJI
if 'krasnale_m1' not in st.session_state:
    st.session_state.zloza_m1 = [Zloze("Z1", "Kopalnia_Z1", 2), Zloze("Z2", "Kopalnia_Z2", 2), Zloze("Z3", "Kopalnia_Z3", 1)]
    st.session_state.krasnale_m1 = [
        Krasnal("K1", "Mędrzec", ["Z1", "Z2"]),
        Krasnal("K2", "Gburek", ["Z2", "Z3"]),
        Krasnal("K3", "Apsik", ["Z1"]),
        Krasnal("K4", "Wesołek", ["Z3"]),
        Krasnal("K5", "Nieśmiałek", ["Z2"])
    ]
    
    # DODANO: Tabela odległości (kosztów)
    st.session_state.tabela_odl = {}
    for k in st.session_state.krasnale_m1:
        for z_id in k.umiejetnosci:
            # Losowa odległość od 1 do 20 km
            st.session_state.tabela_odl[(k.id_krasnala, z_id)] = random.randint(1, 20)

if 'punkty_m2' not in st.session_state:
    st.session_state.punkty_m2 = [(2.0, 3.0), (5.0, 8.0), (1.0, 6.0), (8.0, 2.0), (4.0, 4.0), (7.0, 7.0)]

if 'dekametrowcy' not in st.session_state:
    st.session_state.dekametrowcy = [
        {"imie": "Mędrzec", "glosnosc": 30},
        {"imie": "Gburek", "glosnosc": 45},
        {"imie": "Apsik", "glosnosc": 88},
        {"imie": "Wesołek", "glosnosc": 20},
        {"imie": "Nieśmiałek", "glosnosc": 55},
        {"imie": "Śpioch", "glosnosc": 92},
        {"imie": "Dopey", "glosnosc": 10},
        {"imie": "Strażnik_A", "glosnosc": 40},
        {"imie": "Strażnik_B", "glosnosc": 60},
        {"imie": "Strażnik_C", "glosnosc": 75}
    ]

# ==========================================
# MODUŁ I: PRZYDZIAŁ PRACY (GRAFY)
# ==========================================
if modul == "⚒️ Moduł I: Przydział Pracy (Grafy)":
    st.header("⚒️ Interaktywne Zarządzanie i Przydział Pracy (MCMF)")
    
    col_menu, col_graf = st.columns([1, 2])

    with col_menu:
        st.subheader("⚙️ Zarządzanie Zasobami")
        
        # Sekcja zarządzania złożami
        st.write("**--- Zarządzanie Złożami ---**")
        with st.expander("➕ Dodaj Nowe Złoże"):
            nowe_z_nazwa = st.text_input("Nazwa nowego złoża:", "Kopalnia_Z4")
            nowe_z_wydajnosc = st.number_input("Wydajność złoża:", min_value=1, max_value=10, value=2, key="nowe_z_wyd")
            if st.button("Zatwierdź nowe złoże"):
                nowe_id = f"Z{len(st.session_state.zloza_m1) + 1}"
                while any(z.id_zloza == nowe_id for z in st.session_state.zloza_m1):
                    nowe_id = f"Z{random.randint(10, 99)}"
                st.session_state.zloza_m1.append(Zloze(nowe_id, nowe_z_nazwa, nowe_z_wydajnosc))
                st.success(f"Dodano złoże {nowe_z_nazwa} ({nowe_id})!")
                st.rerun()
        
        zloza_kopia = list(st.session_state.zloza_m1)
        for idx, z in enumerate(zloza_kopia):
            c_input, c_del = st.columns([4, 1])
            with c_input:
                z.wydajnosc = st.number_input(f"Wydajność {z.nazwa} ({z.id_zloza}):", min_value=0, max_value=10, value=int(z.wydajnosc), key=f"wyd_{z.id_zloza}")
            with c_del:
                st.write("<br>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_zloze_{z.id_zloza}"):
                    st.session_state.zloza_m1.pop(idx)
                    for k in st.session_state.krasnale_m1:
                        if z.id_zloza in k.umiejetnosci:
                            k.umiejetnosci.remove(z.id_zloza)
                            # Usuwamy też odległość
                            if (k.id_krasnala, z.id_zloza) in st.session_state.tabela_odl:
                                del st.session_state.tabela_odl[(k.id_krasnala, z.id_zloza)]
                    st.rerun()
        
        st.write("**--- Modyfikacja Krasnali ---**")
        k_id = [k.id_krasnala for k in st.session_state.krasnale_m1]
        wybrany_k_id = st.selectbox("Wybierz krasnala do edycji:", k_id)
        wybrany_k = next(k for k in st.session_state.krasnale_m1 if k.id_krasnala == wybrany_k_id)

        st.write(f"Aktualne umiejętności: `{wybrany_k.umiejetnosci}`")
        
        wszystkie_zloza_ids = [z.id_zloza for z in st.session_state.zloza_m1]
        nowe_umiejetnosci = st.multiselect("Zmień fachy krasnala:", wszystkie_zloza_ids, default=[u for u in wybrany_k.umiejetnosci if u in wszystkie_zloza_ids], key=f"um_{wybrany_k.id_krasnala}")
        
        if st.button("Zatwierdź zmiany fachu"):
            # Generowanie odległości dla nowych fachów
            for fach in nowe_umiejetnosci:
                if (wybrany_k.id_krasnala, fach) not in st.session_state.tabela_odl:
                    st.session_state.tabela_odl[(wybrany_k.id_krasnala, fach)] = random.randint(1, 20)
            
            wybrany_k.umiejetnosci = nowe_umiejetnosci
            st.success(f"Zaktualizowano fachy dla {wybrany_k.imie}!")
            st.rerun()

        st.write("**--- Dodaj Nowego Krasnala ---**")
        nowe_imie = st.text_input("Imię nowego krasnala:")
        nowe_fachy = st.multiselect("Fachy nowego krasnala:", wszystkie_zloza_ids)
        if st.button("Dodaj do królestwa"):
            new_id = f"K{len(st.session_state.krasnale_m1) + 1}"
            while any(k.id_krasnala == new_id for k in st.session_state.krasnale_m1):
                new_id = f"K{random.randint(10, 99)}"
            
            st.session_state.krasnale_m1.append(Krasnal(new_id, nowe_imie, nowe_fachy))
            
            # Generowanie odległości
            for fach in nowe_fachy:
                 st.session_state.tabela_odl[(new_id, fach)] = random.randint(1, 20)
                 
            st.success(f"Dodano krasnala {nowe_imie}!")
            st.rerun()

    with col_graf:
        st.subheader("📊 Sieć Przepływowa (Min. Koszt / Max. Wydobycie)")
        
        if not st.session_state.zloza_m1 or not st.session_state.krasnale_m1:
            st.warning("Do wyznaczenia sieci przepływowej wymagane jest posiadanie przynajmniej 1 złoża i 1 krasnala.")
        else:
            # Przekazanie tabeli odległości do menedżera
            menadzer = MenadzerPrzydzialu(st.session_state.krasnale_m1, st.session_state.zloza_m1, st.session_state.tabela_odl)
            menadzer.buduj_siec()
            
            # DODANO: Użycie algorytmu MCMF zamiast Edmondsa-Karpa
            max_przeplyw, min_koszt = menadzer.oblicz_mcmf()
            
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.metric(label="Maksymalnie zatrudnieni (max_flow)", value=f"{max_przeplyw} krasnali")
            with col_res2:
                st.metric(label="Łączny dystans do pracy (min_cost)", value=f"{min_koszt} km")

            # Rysowanie Grafu
            G = nx.DiGraph()
            pos = {"START": (0, 0), "KONIEC": (3, 0)}
            
            len_k = max(1, len(st.session_state.krasnale_m1) - 1)
            len_z = max(1, len(st.session_state.zloza_m1) - 1)
            
            for i, k in enumerate(st.session_state.krasnale_m1): 
                pos[k.id_krasnala] = (1, 2.5 - i * (5.0 / len_k))
            for i, z in enumerate(st.session_state.zloza_m1): 
                pos[z.id_zloza] = (2, 1.5 - i * (3.0 / len_z))

            for u, edges in menadzer.siec.sasiedztwo.items():
                for e in edges:
                    if e.przepustowosc > 0:
                        # DODANO: Formatowanie etykiet z uwzględnieniem kosztu (odległości)
                        koszt_str = f" | {e.koszt}km" if e.koszt > 0 and u != "START" and e.cel != "KONIEC" else ""
                        G.add_edge(u, e.cel, flow=f"{e.przeplyw}/{e.przepustowosc}{koszt_str}")

            fig, ax = plt.subplots(figsize=(14, 9))
            edge_labels = nx.get_edge_attributes(G, 'flow')
            
            nx.draw_networkx_nodes(G, pos, node_color='#deff9a', node_size=2800, edgecolors='#777777', ax=ax)
            nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=ax)
            
            # Łuki dla lepszej widoczności
            nx.draw_networkx_edges(
                G, pos, edge_color='#777777', arrows=True, arrowsize=15,
                connectionstyle='arc3,rad=0.15', width=1.2, ax=ax
            )
            
            # Etykiety rotowane, przesunięte i z dopasowaniem do łuków
            nx.draw_networkx_edge_labels(
                G, pos, edge_labels=edge_labels, ax=ax, font_color='red', 
                font_weight='bold', font_size=9, label_pos=0.55, rotate=True,
                connectionstyle='arc3,rad=0.15'
            )
            
            ax.set_axis_off()
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)

# ==========================================
# MODUŁ II: PATROL KSIĘCIA (GEOMETRIA)
# ==========================================
elif modul == "🐎 Moduł II: Patrol Księcia (Geometria)":
    st.header("🐎 Konfiguracja i Trasa Patrolu Księcia")
    
    col_punkty, col_mapa = st.columns([1, 1.5])

    with col_punkty:
        st.subheader("📍 Edycja Współrzędnych Kopalń")
        
        st.write("**Dodaj nową kopalnię:**")
        new_x = st.number_input("Współrzędna X:", value=5.0, step=0.5)
        new_y = st.number_input("Współrzędna Y:", value=5.0, step=0.5)
        if st.button("Dodaj kopalnię do mapy"):
            st.session_state.punkty_m2.append((new_x, new_y))
            st.rerun()

        st.write("**Lista kopalń (Modyfikacja / Usuwanie):**")
        punkty_kopia = list(st.session_state.punkty_m2)
        for idx, (x, y) in enumerate(punkty_kopia):
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                edit_x = st.number_input(f"X [{idx+1}]", value=x, key=f"x_{idx}", step=0.1)
            with c2:
                edit_y = st.number_input(f"Y [{idx+1}]", value=y, key=f"y_{idx}", step=0.1)
            with c3:
                st.write("")
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.punkty_m2.pop(idx)
                    st.rerun()
            st.session_state.punkty_m2[idx] = (edit_x, edit_y)

    with col_mapa:
        if len(st.session_state.punkty_m2) < 2:
            st.warning("Dodaj co najmniej 2 kopalnie, aby wyznaczyć trasę patrolu.")
        else:
            otoczka = get_convex_hull(st.session_state.punkty_m2)
            obwod = calculate_perimeter(otoczka)
            
            st.metric(label="Długość muru / obwód patrolu", value=f"{obwod:.2f} metrów")
            
            fig, ax = plt.subplots(figsize=(6, 6))
            px, py = zip(*st.session_state.punkty_m2)
            ax.scatter(px, py, color='#a8cf45', s=120, zorder=3, label="Kopalnie")
            
            if len(otoczka) >= 2:
                ox, oy = zip(*(otoczka + [otoczka[0]]))
                ax.plot(ox, oy, 'r--', linewidth=2.5, zorder=2, label="Trasa Księcia")
                
            for i, p in enumerate(otoczka):
                ax.annotate(f"P_{i+1}", p, textcoords="offset points", xytext=(0,8), ha='center', weight='bold', color='black')

            ax.grid(True, linestyle='--', alpha=0.5)
            ax.legend()
            st.pyplot(fig)

# ==========================================
# MODUŁ III: OBRONA GRANIC (STRUKTURY)
# ==========================================
elif modul == "🛡️ Moduł III: Obrona Granic (Struktury)":
    st.header("🛡️ Interaktywny System Defensywny Granic")
    
    col_ustawienia, col_wykres = st.columns([1, 1.5])

    with col_ustawienia:
        st.subheader("👥 Edycja Drużyny Dekametrowców")
        
        rozmiar_druzyny = st.slider("Liczba krasnali na granicy:", 4, 15, len(st.session_state.dekametrowcy))
        
        while len(st.session_state.dekametrowcy) < rozmiar_druzyny:
            st.session_state.dekametrowcy.append({"imie": f"Strażnik_{len(st.session_state.dekametrowcy)+1}", "glosnosc": 50})
        while len(st.session_state.dekametrowcy) > rozmiar_druzyny:
            st.session_state.dekametrowcy.pop()

        for i in range(rozmiar_druzyny):
            c1, c2 = st.columns([2, 1])
            with c1:
                st.session_state.dekametrowcy[i]["imie"] = st.text_input(f"Imię krasnala {i}", value=st.session_state.dekametrowcy[i]["imie"], key=f"name_m3_{i}")
            with c2:
                st.session_state.dekametrowcy[i]["glosnosc"] = st.number_input(f"Bale (dB) {i}", min_value=1, max_value=120, value=st.session_state.dekametrowcy[i]["glosnosc"], key=f"vol_m3_{i}")

    glosnosci = [k["glosnosc"] for k in st.session_state.dekametrowcy]
    imiona = [k["imie"] for k in st.session_state.dekametrowcy]
    dane_granicy = list(zip(glosnosci, imiona))
    drzewo = DrzewoPrzedzialowe(dane_granicy)

    with col_wykres:
        st.subheader("🏹 Symulator Odparcia Ataku")
        
        st.write("Wybierz obszar uderzenia wroga za pomocą suwaka przedziału:")
        obszar_ataku = st.slider(
            "Zakres metrów granicy:",
            min_value=0,
            max_value=len(glosnosci) - 1,
            value=(0, len(glosnosci) - 1)
        )
        poczatek, koniec = obszar_ataku

        najglosniejszy = drzewo.znajdz_najglosniejszego(poczatek, koniec)

        st.error(f"🚨 ALERT! Wróg uderzył w odcinek od {poczatek} do {koniec} metra granicy!")
        if najglosniejszy[0] != float('-inf'):
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