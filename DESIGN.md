## Classes et Modules Principaux

### 1. `GameView` (hérite de `arcade.View`)
- **Responsabilités** : Vue principale du jeu. Elle orchestre le rendu, l'entrée utilisateur, la mise à jour du monde, le suivi de la caméra, la gestion du score, des vies et du changement de niveau.
- **Méthodes** :
  - `__init__`, `setup`, `on_draw`, `on_update`
  - `on_key_press`, `on_key_release`, `on_mouse_press`, `on_mouse_release`
  - `check_for_gameover`, `run_switch`, `pan_camera_to_player`
- **Concepts appliqués** :
  - SRP (Single Responsibility Principle) : chaque méthode remplit un rôle bien précis.
  - Encapsulation : séparation stricte entre chargement (`MapLoader`), dessin (`MapDrawer`), logique (`update`).


---

### 2. `Entity` (classe abstraite)
- **Responsabilités** : Classe de base pour toutes les entités ennemies dynamiques.
- **Méthodes** :
  - `movement()` (abstraite)
  - `on_update(delta_time)`
- **Concepts appliqués** :
  - Template Method Pattern : `movement()` est une méthode à implémenter dans les sous-classes.
  - Polymorphisme : utilisé de manière interchangeable via `SpriteList[Entity]`.

---

### 3. `Blob`, `Bat`, `Ghost` (héritent d’`Entity`)
- **Responsabilités** :
  - `Blob` : déplacement horizontal avec inversion aux murs ou falaises.
  - `Bat` : mouvement pseudo-aléatoire dans un rayon donné.
  - `Ghost` : poursuite du joueur si à moins de 300px.
- **Méthodes** :
  - `movement()`
- **Concepts appliqués** :
  - `Blob` : cooldown d'inversion pour éviter les mouvements erratiques.
  - `Bat` : stochastique, bruit Gaussien.
  - `Ghost` : calcul vectoriel directionnel.

---

### 4. `Player` (hérite de `arcade.Sprite`)
- **Responsabilités** : Gestion des mouvements, sauts, armes, interactions avec l’environnement et interface utilisateur.
- **Méthodes** :
  - `on_key_press`, `on_key_release`, `on_mouse_press`, `on_mouse_release`
  - `update_player_speed()`
- **Concepts appliqués** :
  - Encapsulation : `sprite_list`, `weapon`, `lives`, `blink_state`.
  - FSM implicite : état interne des touches, gestion de saut.
  - Mécanique d’invincibilité temporaire (clignotement via `hidden_time`).
  - Gestion d’arme dynamique : `sword` vs `bowArrow`.

---

### 5. `Platform`
- **Responsabilités** : Représente une plateforme (fixe ou mobile) et ses bornes de mouvement.
- **Méthodes** :
  - `__init__`, `@property block`, `bound_left`, `bound_right`, `bound_up`, `bound_down`
- **Concepts appliqués** :
  - **Encapsulation forte** : attributs privés avec getters uniquement.
  - **Détection de mouvements** : en fonction des flèches `← ↑ → ↓`.
  - **Utilisée pour collision, gravité, et support dynamique**.

---

### 6. `MapLoader`
- **Responsabilités** : Lire les cartes à partir d’un fichier `.txt` contenant une partie YAML (métadonnées) et une grille ASCII (niveau).
- **Méthodes** :
  - `read_map`, `filepath` (getter + setter)
- **Concepts appliqués** :
  - Séparation des données et du code : configuration YAML.
  - Encapsulation : accès restreint au chemin de fichier (`__filepath`).

---

### 7. `MapDrawer`
- **Responsabilités** : Construire les `SpriteList` du niveau en fonction des données chargées par `MapLoader`.
- **Méthodes** :
  - `entities_to_SpriteList`
  - `Platform_to_SpriteList`
  - `switches_to_SpriteList`
  - `gates_to_SpriteList`
  - `get_collectable_to_SpriteList`
  - `get_exit_to_SpriteList`
- **Concepts appliqués** :
  - Builder Pattern : transforme des données logiques en objets visuels (sprites).
  - Optimisation du rendu via spatial hash et `seen`.

---

### 8. `Collectable` (abstraite), `Coin`, `Apple`
- **Responsabilités** :
  - `Collectable` : interface pour les objets ramassables.
  - `Coin` : augmente le score.
  - `Apple` : rend invincible pendant 3s.
- **Méthodes** :
  - `effect_on_view(view)`, `collect(view)`
- **Concepts appliqués** :
  - Polymorphisme : chaque collectable a un effet différent.

---

### 9. `update.py`
- **Responsabilités** : Centralise les mises à jour du monde à chaque frame (physique, collisions, entités, armes, transitions, plateformes dynamiques).
- **Fonctions** :
  - `on_update(gameview, delta_time)`
  - `get_sprites_movement`
  - `switch_exit_movement`
- **Concepts appliqués** :
  - Gestion dynamique des projectiles (flèches).

---

### 10. `utils.py`
- **Responsabilités** : Fonctions d’aide indépendantes : conversion coordonnées, détection de plateformes, composantes connexes.
- **Fonctions** :
  - `coordinate`, `bfs_connected_components`, `get_platform`, `get_borders`
- **Concepts appliqués** :
  - Fonctions pures : pas d’effet de bord.
  - Testabilité accrue : code réutilisable et découplé.
  - Détection automatique de plateformes via BFS.

---

### 11. `constants.py`

- **Responsabilités** : Fournir toutes les constantes globales nécessaires au fonctionnement du jeu :
  - Paramètres de la fenêtre
  - Vitesse, gravité, taille des tuiles
  - Chemins vers les assetS (joueurs, plateformes, armes, objets)
  - Dictionnaires `ASSETS` et `WEAPON`
  - Enumération `Arrow` pour les directions de déplacement des plateformes

- **Contenu principal** :
  - Constantes numériques : `WINDOW_WIDTH`, `PLAYER_JUMP_SPEED`, `ARROW_GRAVITY`, etc.
  - Dictionnaires :
    - `ASSETS` : mappage entre caractères de carte (`=`, `*`, `S`, `E`, etc.) et chemins vers les sprites
    - `WEAPON` : chemins vers les images d’armes
  - Enumération `Arrow` : utilisée dans la détection de bornes (`← ↑ → ↓`)

- **Concepts appliqués** :
  - Séparation de la configuration et du code métier
  - **Usage de `Final` / `Enum`** pour garantir l'immuabilité et la clarté des types
  - Centralisation des chemins d’assets permet une gestion centralisée des ressources graphiques

---

### 12. `main.py`

- **Responsabilités** : Point d’entrée du programme.
  - Initialise Arcade
  - Crée une instance de `GameView`
  - Lance la boucle principale

- **Méthodes / Contenu** :
  - `if __name__ == "__main__":`
    - Appel à `arcade.Window(...)`
    - Initialisation de la vue avec `GameView("maps/map1.txt")`
    - Lancement avec `arcade.run()`

- **Concepts appliqués** :
  - **Pattern standard Python d’exécution (`__main__`)**
  - Inversion de dépendance : `main.py` ne connaît que `GameView`, mais pas la logique interne.
  - **Responsabilité minimale** : juste la mise en route du jeu.

## Interactions entre Classes, Méthodes et Modules



🔁 Interactions entre Classes, Méthodes et Modules

## Vue centrale : `GameView`
  - Le `Player` (mouvement, entrées clavier/souris)
  - Les entités `Entity` (`Blob`, `Bat`, `Ghost`) via `entity_list`
  - Les plateformes, objets et éléments de décor (via `MapDrawer`)
  - La lecture du niveau (via `MapLoader`)
  - La logique du jeu (via `update.on_update`)
  - Le calcul des plateformes : `utils.get_platform(...)`
  - Le placement des objets : `MapDrawer.*_to_SpriteList()`
  - Le comportement des objets collectés : `collectable.Collectable.effect_on_view()`
  - La détection d'interactions (`switch`, `exit`, `lava`, `monstres`) à `update.py`

---

### `Player`
- Appelé par `GameView` dans :
  - `on_key_press`, `on_mouse_press`, `check_for_gameover`, `on_update`
- Interaction avec :
  - `weapon` (liste de `Sprite`) et `sprite_list`
  - `camera` pour viser avec la souris
  - `Collectable` pour activer `effect_on_view()`
  - `switch` et `gate` (via armes et collisions)

---

### `Entity`, `Blob`, `Bat`, `Ghost`
- Appelés par: `update.on_update()` → `entity.on_update(delta_time)`
- Ont accès à:
  - `self.game.wall_list` pour détecter les collisions (via `GameView`)
  - `self.game.player` pour interagir (ex: `Ghost`)
- Comportement polymorphe : tous possèdent `movement()`, mais l’implémentation est spécifique.

---

### `MapLoader` ↔ `MapDrawer`
- MapLoader.read_map()` retourne :
  - `width`, `height`, `map_data`, `switches`, `gates`, `next_map`
- `MapDrawer`consomme ces données pour construire :
  - `entity_list`, `platform_list`, `gate_list`, `switch_list`, `collectable_list`, `exit_list`

---

### `update.py`
- Appelé dans : `GameView.on_update(delta_time)`
- Coordonne :
  - `physics_engine.update()`
  - Mise à jour des entités (`entity.on_update`)
  - Armes et collisions (`weapon`, `arrow`, `sword`)
  - Détection de fin de niveau ou game over
  - Activation des `switches` (via `run_switch`)
- Utilise:
  - `get_sprites_movement()` : pour suivre les plateformes
  - `switch_exit_movement()` : repositionne objets liés aux plateformes

---

### `Collectable`, `Coin`, `Apple`
- Instanciés par : `MapDrawer.get_collectable_to_SpriteList()`
- Collectés dans : `update.on_update()` → `collectable.collect(GameView)`
- Appellent : `effect_on_view(GameView)` pour déclencher :
  - `score += 1` (`Coin`)
  - `invincibilité temporaire` (`Apple`)

---

### `utils.py`
- Appelé par :
  - `GameView.setup()` : `get_platform()`, `coordinate()`
  - `MapDrawer` : `get_borders()`, `bfs_connected_components()`
- Indépendant : aucune dépendance circulaire, code pur.

---

### Fichiers YAML
- Chargés par : `MapLoader.read_map()`
- Contiennent :
  - les dimensions
  - les `switches` et `gates` + leurs actions (`open-gate`, `close-gate`, `disable`)
  - la carte ASCII du niveau
- Utilisés pour générer :
  - les éléments interactifs (`^`, `|`)
  - les entités (`o`, `v`, `G`)
  - les objets (`*`, `p`)







  ## Diagramme de structure

                            +-----------------+
                            |    Entity       |◄────────┐
                            |-----------------+         │
                            | + movement()     |         │
                            +-----------------+         │
                              ▲       ▲         ▲        │
     +---------+       +----------+  +-------+  +--------+
     |  Blob   |       |   Bat    |  | Ghost |  |Player  |
     |---------|       |----------|  |-------|  |--------|
     |movement |       |movement  |  |move() |  |input() |
     +---------+       +----------+  +-------+  +--------+
                                                   ▲
                                                   │
                            +----------------------+-------------+
                            |           GameView                 |
                            |------------------------------------|
                            | + setup(), on_draw(), run_switch() |
                            | + player : Player                  |
                            | + entity_list : List[Entity]       |
                            +----------------------+-------------+
                                                   ▲
         ┌─────────────────────────────────────────┼─────────────────────────────────────┐
         │                                         │                                     │
+----------------+               +--------------------+           +----------------+   +----------------+
|   MapLoader    |               |     MapDrawer      |           |  update.py     |   |   utils.py     |
|----------------|               |--------------------|           |----------------|   |----------------|
| read_map()     |──┐     ┌─────▶| build sprites      |◄──────────| on_update()    |   | bfs(), get_pl. |
+----------------+  │     │      +--------------------+           +----------------+   +----------------+
                    │     │
                    ▼     ▼
              +----------------+
              |  YAML map file |
              |----------------|
              | width, gates,  |
              | switches, map  |
              +----------------+

+-----------------+           +----------------+           
|  Collectable    |◄──────────| Coin / Apple   |
|-----------------|           |----------------|
| +effect_on_view |           | +score / heal  |
+-----------------+           +----------------+
