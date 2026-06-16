import matplotlib.pyplot as plt

krasnale = [100, 1000, 5000, 10000, 20000]
zloza = [50, 500, 1000, 2000, 4000]
czasy = [0.0980, 3.9080, 11.9962, 53.7679, 326.6212]

plt.figure(figsize=(10, 6))
plt.plot(krasnale, czasy, marker='o', linestyle='-', color='#2c3e50', linewidth=2)

# Dodanie adnotacji (K, Z) dla każdego punktu
for i in range(len(krasnale)):
    plt.annotate(f"K:{krasnale[i]}\nZ:{zloza[i]}", 
                 (krasnale[i], czasy[i]), 
                 textcoords="offset points", 
                 xytext=(0, 15), 
                 ha='center',
                 fontsize=9,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

plt.title('Wydajność algorytmu Edmondsa-Karpa w zależności od liczby krasnali (K) i złóż (Z)', fontsize=14)
plt.xlabel('Liczba krasnoludków ($K$)', fontsize=12)
plt.ylabel('Czas obliczeń ($s$)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig('wykres_wydajnosci_kompletny.png')
print("Wykres kompletny został zapisany.")