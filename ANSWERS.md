# ANSWERS.md

Ce document répond point par point aux questions posées dans les instructions hebdomadaires du projet, en s’appuyant sur la conception et le code fournis.

---

## 1. Comment avez-vous conçu la lecture du fichier ? Comment l’avez-vous structurée de sorte à pouvoir la tester de manière efficace ?

La lecture du fichier a été conçue autour de la classe `MapLoader`. Elle est responsable de :
- Séparer la partie configuration YAML et la partie carte ASCII grâce au séparateur `---`.
- Charger la configuration (dimensions, carte suivante, interrupteurs, portes) avec PyYAML pour permettre une manipulation structurée et typée.
- Analyser les interrupteurs et les portes en explicitant tous les champs attendus et en traitant les valeurs par défaut.
- Normaliser chaque ligne de la carte ASCII pour garantir une largeur homogène (avec `ljust(width)`), facilitant ainsi la gestion des coordonnées.
- Retourner la carte sous forme de liste de chaînes inversée (ligne du bas en premier), ce qui simplifie la correspondance avec le repère du jeu et les tests de collisions.

Pour rendre la lecture testable :
- La méthode `read_map` retourne tous les éléments utiles dans un tuple, ce qui permet de tester séparément la configuration, les interrupteurs, les portes et la carte.
- La classe permet de changer dynamiquement le chemin du fichier via une propriété, ce qui rend les tests unitaires et paramétrés faciles à écrire.
- Les exceptions sont déclenchées en cas d’entrée invalide (ex: mauvais chemin, séparateur absent), ce qui permet de tester les cas d’erreur.

---

## 2. Comment avez-vous adapté vos tests existants au fait que la carte ne soit plus la même qu’au départ ? Est-ce que vos tests résisteront à d’autres changements dans le futur ? Si oui, pourquoi ? Si non, que pensez-vous faire plus tard ?

Pour adapter les tests :
- Les tests ne reposent plus sur des indices de lignes ou de colonnes fixes ni sur des chaînes brutes, mais sur les valeurs lues et structurées par `MapLoader`.
- Chaque test crée dynamiquement un fichier de carte complet (en-tête YAML et carte ASCII) avant l’exécution du test, ce qui garantit l’isolation et la reproductibilité.
- La configuration YAML et la carte ASCII sont testées indépendamment, ce qui permet d’ajouter ou de modifier des champs sans impacter les tests existants.
- On vérifie que les dimensions, les switches, les gates et la carte sont correctement extraits et interprétés.

Résistance aux changements futurs :
- OUI, les tests sont conçus pour tolérer l’ajout de nouveaux champs dans la configuration YAML grâce à l’utilisation de `dict.get()`.
- La structure de la carte peut évoluer (ajout de nouveaux symboles, modification de la largeur/hauteur), les tests s’adapteront tant que le format (YAML + `---` + ASCII) est respecté.
- En cas d’évolution profonde du format, il suffira de modifier les fichiers de tests, sans avoir à toucher à la logique de test elle-même.
- Si des changements importants sont prévus (nouveaux types d’objets, nouveaux comportements), on prévoit d’ajouter des tests de non-régression et de couverture pour chaque nouveauté.

---

## 3. Le code qui gère la lave ressemble-t-il plus à celui de l’herbe, des pièces, ou des blobs ? Expliquez votre réponse.

Le code qui gère la lave ressemble davantage à celui de l’herbe ou des pièces, pas à celui des blobs :
- L’herbe (`=`), la lave (`£`) et les pièces sont tous des objets de type "statique" : ils existent à des positions fixes sur la carte, sont chargés lors de la lecture du fichier, et leur gestion repose sur une simple détection de collision ou de contact.
- Comme pour l’herbe, le traitement de la lave consiste simplement à vérifier si le joueur entre en collision avec une case contenant le symbole `£` et à appliquer l’effet associé (perte de vie, respawn, etc.).
- Les blobs, au contraire, sont des entités dynamiques dotées d’une logique de déplacement, d’inversion de direction et d’un cycle de vie autonome (cf. leur méthode `movement`).
- La lave n’a pas de logique de déplacement ou de comportement propre : elle ne fait que réagir au passage du joueur, ce qui la rapproche de la gestion de l’herbe et des pièces.

---

## 4. Comment détectez-vous les conditions dans lesquelles les blobs doivent changer de direction ?

La détection du changement de direction des blobs repose sur deux mécanismes dans la méthode `movement` :
1. **Collision frontale avec un mur** :
   - On utilise `arcade.check_for_collision_with_list(self, self.game.wall_list)` pour vérifier si le blob touche un mur devant lui.
   - Si une collision est détectée, on inverse la direction de déplacement (`self.change_x = -self.change_x`) et on applique un court "cooldown" pour éviter de rebondir plusieurs fois de suite sur le même mur.

2. **Absence de sol devant le blob (risque de tomber)** :
   - On teste si, juste devant le blob, il n’y a plus de bloc solide sous ses pieds en regardant les points `(left_hitbox, self.bottom - 1)` et `(right_hitbox, self.bottom - 1)`.
   - Si le blob avance vers la droite et qu’il n’y a pas de sol à droite (`not ground_right`), il fait demi-tour à gauche, et inversement pour la gauche.
   - Cela permet au blob de "patrouiller" sur une plateforme sans en tomber.

Ainsi, un blob change de direction soit lorsqu’il heurte un obstacle, soit lorsqu’il risque de tomber dans le vide.


# Réponses aux questions hebdomadaires (semaine épée, score, next-map, etc.)

---

### 1. Quelles formules utilisez-vous exactement pour l’épée ? Comment passez-vous des coordonnées écran aux coordonnées monde ?

Pour l’épée, nous utilisons :

- **Transformation coordonnées** :  
  Lors d’un clic souris, on convertit les coordonnées écran `(x, y)` en coordonnées monde `(world_x, world_y)` grâce à `camera.unproject((x, y))`.  
  Cela permet d’adapter l’angle et la position de l’épée par rapport à la position réelle de la joueuse dans le monde du jeu, indépendamment du défilement de la caméra.

- **Angle de frappe** :  
  ```python
  angle = 45 - math.degrees(math.atan2(world_y - self.center_y, world_x - self.center_x))
  self.sword.angle = angle
  ```
  Cette formule donne l’angle entre la joueuse et le curseur, ce qui oriente l’épée dans la direction du clic.

- **Position de l’épée** :  
  - Si le clic est à droite de la joueuse : l’épée apparaît à droite (`self.sword.center_x = self.right + 10`)
  - Sinon à gauche (`self.sword.center_x = self.left - 10`)
  - L’ordonnée est centrée sur la joueuse.

---

### 2. Comment testez-vous l’épée ? Comment testez-vous que son orientation est importante pour déterminer si elle touche un monstre ?

- **Test unité de collision** :  
  On place des monstres à des positions différentes autour de la joueuse.
  - On simule un clic dans différentes directions et on vérifie que seuls les monstres dans la direction de l’épée sont retirés (collision détectée).
  - On utilise `arcade.check_for_collision_with_list(self.sword, self.entity_list)` juste après avoir donné l’angle à l’épée.

- **Test orientation** :  
  - On vérifie qu’en frappant à droite, un monstre à gauche n’est pas touché et vice versa.
  - On automatise ces tests en “cliquant” virtuellement à différents endroits autour de la joueuse et en inspectant la liste des entités restantes.

- **Test d’angle** :  
  - On vérifie que l’angle calculé correspond à la direction attendue (ex : clic au-dessus = angle ~90°, clic à droite = angle ~0°).

- **Test de timing** :  
  - On s’assure que la fenêtre de collision (0.2s) fonctionne : le monstre doit être touché uniquement si l’épée vient d’être “dessinée”.

---

### 3. Comment transférez-vous le score de la joueuse d’un niveau à l’autre ?

- Le score est un attribut de l’objet `GameView` (`self.score`).
- Avant de passer au niveau suivant (dans la détection de collision avec l’exit), on conserve `gameview.score` et on relance la méthode `setup(self.next_map)` sans réinitialiser cet attribut.
- Ainsi, le score n’est jamais réinitialisé lors du changement de carte, il est simplement incrémenté ou utilisé tel quel lors du passage au niveau suivant.

---

### 4. Où le remettez-vous à zéro ? Avez-vous du code dupliqué entre les cas où la joueuse perd parce qu’elle a touché un monstre ou de la lave ?

- **Remise à zéro du score** :  
  - Le score est remis à zéro dans :
    - `check_for_gameover()` quand la joueuse touche de la lave (`self.score = 0`)
    - ou quand elle perd toutes ses vies (`self.score = 0`)
    - aussi dans `on_key_press` lors d’un “reset” manuel (touche espace).
- **Code dupliqué** :  
  - Oui, la logique de remise à zéro du score et de réinitialisation du niveau (`self.setup()`) est présente dans plusieurs cas (lave, vie = 0, touche espace).
  - Pour l’instant, la duplication est limitée et rend le flux explicite (chaque cause de gameover relance la partie).
  - À l’avenir, pour éviter toute incohérence, on pourrait factoriser cette logique dans une seule méthode (`reset_game()`).

---

### 5. Comment modélisez-vous la “next-map” ? Où la stockez-vous, et comment la traitez-vous quand la joueuse atteint le point E ?

- **Modélisation** :  
  - Le champ `next-map` est lu depuis le YAML de la carte lors du chargement (`self.next_map = next_map`).
  - Il est stocké comme attribut de l’objet `GameView`.
- **Traitement** :  
  - Lors d’une collision avec le sprite de sortie (`exit_list`), on appelle :
    ```python
    gameview.current_lives = gameview.player.lives
    gameview.setup(gameview.next_map)
    ```
    Ce qui recharge la nouvelle carte indiquée par `next_map`, tout en conservant le score et le nombre de vies.

---

### 6. Que se passe-t-il si la joueuse atteint le E mais la carte n’a pas de next-map ?

- Si la carte n’a pas de champ `next-map` ou que celui-ci est vide, la méthode `setup(gameview.next_map)` échoue (car le fichier n’existe pas ou le chemin est vide).
- Pour éviter un crash, il y a un `try...except` autour de ce rechargement :  
  - Si une exception est levée (fichier absent), on appelle `arcade.exit()` pour quitter proprement le jeu.
- Ainsi, le jeu se termine automatiquement si la dernière carte ne spécifie pas de `next-map`.

# Réponses - Semaine Arc, Flèches, Chauves-souris, Gestion des monstres & armes

---

### 1. Quelles formules utilisez-vous exactement pour l’arc et les flèches ?

- **Angle de tir** :  
  Lorsqu’on clique, on calcule l’angle entre la joueuse et le pointeur souris :
  ```python
  bowArrow_angle = -math.degrees(math.atan2(y - self.center_y, x - self.center_x))
  self.bowArrow.angle = bowArrow_angle
  ```
- **Vitesse de la flèche** :  
  Lors du relâchement de la souris, la flèche est créée à la position de la joueuse, avec une vitesse dépendant de l’angle :
  ```python
  arrow_angle = -math.degrees(math.atan2(self.arrow_target_y - self.center_y, self.arrow_target_x - self.center_x))
  new_arrow.change_x = ARROW_SPEED * math.cos(math.radians(arrow_angle))
  new_arrow.change_y = -ARROW_SPEED * math.sin(math.radians(arrow_angle))
  ```
- **Gravité** :
  À chaque frame, la gravité est appliquée à la flèche :
  ```python
  arrow.change_y -= ARROW_GRAVITY
  ```

---

### 2. Quelles formules utilisez-vous exactement pour le déplacement des chauves-souris (champ d’action, changements de direction, etc.) ?

- **Champ d’action** :  
  La chauve-souris reste dans un cercle de rayon 200 pixels autour de son point de départ :
  ```python
  if sqrt((self.starting_x - self.center_x)**2 + (self.starting_y - self.center_y)**2) <= 200:
  ```
- **Déplacement aléatoire** :  
  Elle ajoute une petite variation aléatoire (loi normale) à sa vitesse chaque frame :
  ```python
  self.change_x += random.normalvariate(0, 0.05)
  self.change_y += random.normalvariate(0, 0.05)
  ```
  Si la vitesse devient trop élevée (abs > 0.5), elle est réduite :
  ```python
  if abs(self.change_x) > 0.5: self.change_x *= 0.25
  if abs(self.change_y) > 0.5: self.change_y *= 0.25
  ```
- **Retour au centre** :  
  Si elle sort de la zone d’action, elle est "rappelée" au point de départ :
  ```python
  self.change_x = -(self.center_x - self.starting_x) * 0.007
  self.change_y = -(self.center_y - self.starting_y) * 0.007
  ```

---

### 3. Comment avez-vous structuré votre programme pour que les flèches puissent poursuivre leur vol ?

- **Gestion des flèches** :  
  Les flèches sont des sprites ajoutés à `sprite_list` de la joueuse.  
  À chaque frame (dans la boucle d’update du jeu), on parcourt la sprite_list :
  - On actualise la position des flèches selon leur vitesse et la gravité.
  - On supprime les flèches si elles sortent de l’écran, touchent un mur, de la lave, un monstre, un switch, ou une plateforme.
  - Si une flèche touche un monstre, le monstre est retiré du jeu.
  - Chaque flèche a sa propre vitesse (change_x, change_y) et continue son vol jusqu’à une collision ou sortie d’écran.
- **Indépendance** :  
  Les flèches ne bloquent pas le déroulement du jeu et n’interagissent qu’au moment de la collision.

---

### 4. Comment gérez-vous le fait que vous avez maintenant deux types de monstres, et deux types d’armes ? Comment faites-vous pour ne pas dupliquer du code entre ceux-ci ?

- **Hiérarchie de classes** :  
  - Les deux types de monstres (`Blob`, `Bat`) héritent d’une classe commune `Entity`, qui factorise tout le comportement général (affichage, update, collisions).
  - Les méthodes spécifiques (`movement`) sont surchargées dans chaque sous-classe.
- **Armes** :  
  - Les armes (`sword`, `bowArrow`) sont gérées comme des objets dans une liste `self.weapon` associée à la joueuse.
  - La logique d’attaque (calcul de la direction, ajout à la sprite_list, collision) est mutualisée et dépend seulement de l’arme active.
- **Gestion des collisions** :  
  - La détection de collision entre armes et monstres repose sur `arcade.check_for_collision_with_list`, qui est indépendante du type précis de l’arme ou du monstre.
  - L’effet (tuer le monstre) est le même quelle que soit l’arme utilisée, ce qui évite la duplication.
- **Switch d’arme** :  
  - Le changement d’arme se fait via un index (`active_weapon_index`), ce qui permet d’ajouter d’autres armes facilement sans dupliquer le code de gestion des entrées.
- **Conclusion** :  
  - Toute la logique générique est factorisée dans des méthodes partagées ou des classes parentes.
  - Les exceptions (comportements différents) sont traitées localement dans les sous-classes ou via des if spécifiques si besoin.   
   
# Réponses aux questions - Plateformes, interrupteurs, design général
---

### 1. Quel algorithme utilisez-vous pour identifier tous les blocs d’une plateforme, et leurs limites de déplacement ?

Pour identifier tous les blocs d’une plateforme, j’utilise un **BFS (Breadth-First Search)** à partir d’un point de la plateforme :  
- On explore toutes les cases adjacentes faisant partie de la même plateforme (mêmes caractères : `-`, `=`, `£`, `x`), en évitant les éléments non plateformes (interrupteurs, pièces, spawn, portes, etc.).
- Tous les blocs trouvés forment la composante connexe considérée comme une plateforme.

Pour déterminer les **limites de déplacement** :
- On regarde autour de chaque bloc de la plateforme.
- Si on trouve une série de flèches (`←`, `→`, `↑`, `↓`), on avance dans la direction de la flèche pour trouver la limite extrême atteignable dans cette direction.
- Ces bornes sont stockées dans un dictionnaire associant chaque direction à l’abscisse/ordonnée limite.

---

### 2. Sur quelle structure travaille cet algorithme ? Quels sont les avantages et inconvénients de votre choix ?

L’algorithme travaille sur une **liste de chaînes de caractères** (`map_data`), chaque chaîne représentant une ligne de la carte.

**Avantages** :
- Facile à manipuler : chaque case est accessible par `map_data[y][x]` (indices entiers).
- Permet une représentation fidèle à la carte ASCII utilisée dans les fichiers et donc une grande lisibilité.
- Rapide pour parcourir et modifier la carte lors de l’analyse.

**Inconvénients** :
- Pas d’encapsulation : il faut faire attention à l’indice `y` (ligne) vs `x` (colonne).
- L’accès n’est pas typé ni sécurisé (une faute d’indice lève une exception).
- Si la carte était très grande, manipuler des listes de chaînes serait moins efficace que des structures numpy ou des objets plus spécialisés.

---

### 3. Quelle bibliothèque utilisez-vous pour lire les instructions des interrupteurs ? Dites en une ou deux phrases pourquoi vous avez choisi celle-là.

J’utilise la bibliothèque **PyYAML** (`yaml.safe_load`) pour lire les instructions des interrupteurs à partir de la partie YAML des fichiers de carte.  
Ce choix s’explique par la simplicité d’utilisation, la compatibilité directe avec les dictionnaires Python, et la possibilité de structurer clairement les paramètres complexes des switches (actions multiples, états, etc.) dans le fichier de configuration.

---

### 4. Comment votre design général évolue-t-il pour tenir compte des interrupteurs et des portails ?

Le design général a évolué :
- **Ajout d’une phase de lecture de configuration** (via `MapLoader`) qui extrait switches et gates de la carte et les associe à leurs coordonnées.
- **Gestion centralisée des états** : l’état des interrupteurs est maintenu dans des dictionnaires accessibles globalement, ce qui permet d’appliquer facilement les actions (ouvrir/fermer un portail, désactiver un switch).
- **Séparation des responsabilités** : la création des sprites d’interrupteurs/portes est centralisée dans la classe `MapDrawer`, ce qui permet de dissocier la logique de lecture, d’affichage et d’interaction.
- **Réactivité** : lors de l’interaction avec un interrupteur, le code met à jour l’état des portails ou de l’interrupteur en temps réel, ce qui permet de synchroniser visuellement et logiquement la carte.

En résumé, le code est devenu plus modulaire, chaque entité (plateforme, interrupteur, portail…) ayant ses propres méthodes de lecture, création, et gestion d’état, ce qui facilite l’extension et la maintenance du projet.

---

