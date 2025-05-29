import matplotlib.pyplot as plt
import numpy as np

# ---- Données pour le chargement (blocks) ----
N_blocks = np.array([1, 3, 5, 10, 50, 100, 500, 1000, 10000])
T_blocks = np.array([
    0.001594, 0.001258, 0.001337, 0.001224, 0.001264,
    0.001015, 0.001099, 0.001130, 0.006278
])

# ---- Données pour le chargement (monsters) ----
N_monsters = np.array([1, 3, 5, 10, 50, 100, 500, 1000, 10000])
T_monsters = np.array([
    0.001041, 0.001221, 0.001528, 0.001058, 0.000865,
    0.001117, 0.000994, 0.001262, 0.006719
])

# ---- Données pour on_update (blocks) ----
N_blocks_update = np.array([1, 3, 5, 10, 50, 100, 500, 1000, 10000])
ms_blocks = np.array([
    1.3612, 1.5506, 1.3878, 1.1465, 1.0261,
    1.2107, 0.8210, 3.1848, 1.0399
])

# ---- Données pour on_update (monsters) ----
N_monsters_update = np.array([1, 3, 5, 10, 50, 100, 500, 1000, 10000])
ms_monsters = np.array([
    1.3066, 1.1049, 1.2340, 1.9923, 31.8117,
    102.3707, 202.9097, 374.0869, 3774.6083
])

# ---- GRAPHIQUE 1 : Temps de chargement (blocks vs monsters, log-log) ----
plt.figure(figsize=(7,5))
plt.plot(N_blocks, T_blocks, marker='o', label="Blocks (murs)")
plt.plot(N_monsters, T_monsters, marker='s', label="Monsters (ennemis)")
plt.xscale('log')
plt.yscale('log')
plt.xlabel("Nombre d'éléments (log)")
plt.ylabel("Temps de chargement (s, log)")
plt.title("Temps de chargement vs nombre d'éléments (log-log)")
plt.legend()
plt.grid(True, which="both", ls="--")
plt.tight_layout()
plt.savefig("chargement_loglog.png", dpi=150)
plt.show()

# ---- GRAPHIQUE 2 : Temps moyen on_update (blocks vs monsters, log-log) ----
plt.figure(figsize=(7,5))
plt.plot(N_blocks_update, ms_blocks, marker='o', label="Blocks (murs)")
plt.plot(N_monsters_update, ms_monsters, marker='s', label="Monsters (ennemis)")
plt.xscale('log')
plt.yscale('log')
plt.xlabel("Nombre d'éléments (log)")
plt.ylabel("Temps moyen par frame (ms, log)")
plt.title("Temps on_update vs nombre d'éléments (log-log)")
plt.legend()
plt.grid(True, which="both", ls="--")
plt.tight_layout()
plt.savefig("onupdate_loglog.png", dpi=150)
plt.show()