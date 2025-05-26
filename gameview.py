from __future__ import annotations
from typing import Final , TypedDict, Literal
import arcade
import math
from Entity import Entity ,Blob , Bat ,Ghost
from enum import Enum
from arcade import Rect
import time
import yaml
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
PLAYER_MOVEMENT_SPEED = 5
"""Lateral speed of the player, in pixels per frame."""
PLATFORM_MOVEMENT_SPEED_L = 1
"""Lateral speed of the platform, in pixels per frame."""
PLATFORM_MOVEMENT_SPEED_V = 0.5
"""Vertical speed of the platform, in pixels per frame."""
PLAYER_GRAVITY = 1
"""Gravity applied to the player, in pixels per frame²."""
PLAYER_JUMP_SPEED = 18
"""Instant vertical speed for jumping, in pixels per frame."""
ARROW_GRAVITY = 0.2
ARROW_SPEED = 15
ASSETS = {
    "=": ":resources:/images/tiles/grassMid.png",
    "-": ":resources:/images/tiles/grassHalf_mid.png",
    "x": ":resources:/images/tiles/boxCrate_double.png",
    "*": ":resources:/images/items/coinGold.png",
    "p": "assets/kenney-voxel-items-png/apple.png",
    "£": ":resources:/images/tiles/lava.png",
    "S": ":resources:/images/animated_characters/female_person/femalePerson_idle.png",
    "E": ":resources:/images/tiles/signExit.png" ,
    "^": ":resources:/images/tiles/leverLeft.png", #left par defaut
    "|":":resources:/images/tiles/stoneCenter_rounded.png"
}
WEAPON = {
    "sword" : "assets/kenney-voxel-items-png/sword_bronze.png",
    "bow" : "assets/kenney-voxel-items-png/bow.png",
    "arrow" : "assets/kenney-voxel-items-png/arrow.png",
    "bowArrow" : "assets/kenney-voxel-items-png/bowArrow.png"
}
class ACTION(TypedDict):
    x: int
    y: int
    action: Literal["open-gate", "close-gate", "disable"]

class SWITCH(TypedDict, total = False):
    x: int
    y: int
    state: Literal["on", "off"]
    switch_on: list[ACTION]
    switch_off: list[ACTION]
    enabled: bool

class GATE(TypedDict, total = False):
    x: int
    y: int
    state: Literal["open", "closed"]

class GameView(arcade.View):
    """Main in-game view."""
    player_sprite: arcade.Sprite
    Entities: arcade.SpriteList[Entity]
    player_sprite_list : arcade.SpriteList[arcade.Sprite]
    wall_list: arcade.SpriteList [arcade.Sprite]
    physics_engine : arcade.PhysicsEnginePlatformer
    camera : arcade.camera.Camera2D
    coin_list : arcade.SpriteList[arcade.Sprite]
    powerup_list : arcade.SpriteList[arcade.Sprite]
    lava_list : arcade.SpriteList[arcade.Sprite]
    exit_list : arcade.SpriteList[arcade.Sprite]   
    platform_list : arcade.SpriteList[arcade.Sprite]
    switch_list : arcade.SpriteList[arcade.Sprite]
    gate_list : arcade.SpriteList[arcade.Sprite]
    heart_list : arcade.SpriteList[arcade.Sprite]
    score : int

    def __init__(self) -> None:
        # Magical incantion: initialize the Arcade view
        super().__init__()

        # Choose a nice comfy background color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE
        self.max_lives = 3

        # Setup our game
        self.setup()
        #Track the current state of what key is pressed 
        self.left_pressed = False 
        self.right_pressed = False
        self.up_pressed = False
        self.can_jump = True

        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav", streaming=False)
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav", streaming= False)
        self.gameover_sound = arcade.load_sound(":resources:sounds/gameover1.wav", streaming = False)
        self.next_level = arcade.load_sound(":resources:/sounds/upgrade1.wav", streaming= False)
        
        self.blink_state = True
        self.game_over = False
        self.game_over_time : float = 0.0

        self.lives = self.max_lives
        self.score = 0
        self.hidden_time : float = 0
        self.camera_score = arcade.camera.Camera2D()
        self.camera = arcade.camera.Camera2D()

        from typing import Optional
        self.sword_draw_time: Optional[float] = None  # Track when the sword was drawn

    

    @staticmethod
    def read_map(file_path: str) -> tuple[int, int, list[str], str, list[SWITCH], list[GATE]]:
        """read and analyse the map."""
    
        with open(file_path, 'r', encoding="utf-8", newline='\n') as f:
            lines =f.readlines()

        sep_index = None
        for idx, line in enumerate(lines):
            if line.strip() == "---":
                sep_index = idx
                break

        if sep_index is None:
            raise ValueError("No map separator '---' found in file")
        
        yaml_text = "".join (lines[:sep_index])
        config  = yaml.safe_load(yaml_text)
        # Configuration
        width = config.get("width",0)
        height = config.get("height",0)
        next_map = config.get("next_map"," ")
        switches_ = config.get("switches", [])
        gates = config.get("gates", [])


        switches : list[SWITCH] = []
        for yaml_switch in switches_:
            x = int(yaml_switch["x"])
            y = int(yaml_switch["y"])
            state = yaml_switch.get("state", "off")
            print(x, y, state)
            # Correct: use the YAML state if present, otherwise default to "off"
            if state is True:
                state = "on"
            # Ensure state is always a string and not None
            state = str(state)

            switch_on: list[ACTION] = []
            for action in yaml_switch.get("switch_on", []):
                if action["action"] == "disable":
                    switch_on.append({"x": x, "y": y, "action": "disable"})  # ← coordonnées du switch
                else:
                    switch_on.append({
                        "x": int(action["x"]),
                        "y": int(action["y"]),
                        "action": action["action"],
                    })

            switch_off: list[ACTION] = []
            for action in yaml_switch.get("switch_off", []):
                if action["action"] == "disable":
                    switch_off.append({"x": x, "y": y, "action": "disable"})  # ← coordonnées du switch
                else:
                    switch_off.append({
                        "x": int(action["x"]),
                        "y": int(action["y"]),
                        "action": action["action"],
                    })

            switches.append({
                "x": x,
                "y": y,
                "state": state,  # This will now correctly be "on" if set in YAML
                "switch_on": switch_on,
                "switch_off": switch_off,
                "enabled": True,
            })

        idx += 1
        map_data = []

        # Characters
        while idx < len(lines)  and lines[idx].rstrip() != "---":
            lines[idx] = lines[idx].rstrip().ljust(width)
            map_data.append(lines[idx])
            idx += 1
                   
        map_data = list(reversed(map_data))
        return width, height, map_data, next_map, switches, gates

    @staticmethod
    def coordinate(x: float, tile_size: int = 64) -> float:
        """Convert tile coordinates to pixel coordinates."""
        return x * tile_size + tile_size // 2

    def setup(self, file_path: str = "maps/map1.txt") -> None:
        """Set up the game here."""
        self.player_sprite_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.coin_list = arcade.SpriteList(use_spatial_hash=True)
        self.powerup_list = arcade.SpriteList(use_spatial_hash=True)
        self.lava_list = arcade.SpriteList(use_spatial_hash=True)
        self.exit_list = arcade.SpriteList(use_spatial_hash=True)
        self.Entities = arcade.SpriteList()
        self.platform_list = arcade.SpriteList(use_spatial_hash=True)
        self.switch_list = arcade.SpriteList(use_spatial_hash=True)
        self.gate_list = arcade.SpriteList(use_spatial_hash=True)
        self.switch_infos: dict[tuple[int, int], SWITCH] = {}  # Ensure attribute exists before use
        self.sprite_to_switch_info: dict[arcade.Sprite, SWITCH] = {}
        self.heart_list = arcade.SpriteList(use_spatial_hash=True)

        for i in range(self.max_lives):
            heart = arcade.Sprite("assets/heart.png", scale=0.09)
            heart.center_x = WINDOW_WIDTH - 240 - i * 53
            heart.center_y = WINDOW_HEIGHT - 180
            self.heart_list.append(heart)

        self.sword = arcade.Sprite(
            WEAPON["sword"],
            scale=0.5 * 0.7,
        )

        self.bowArrow = arcade.Sprite(
            WEAPON["bowArrow"],
            scale=0.5 * 0.7,
        )
        self.weapon = [self.sword, self.bowArrow]
        self.active_weapon_index = 1
        self.active_weapon_sprite = self.bowArrow
        class Arrow(Enum):
            LEFT = "←"
            RIGHT = "→"
            UP = "↑"
            DOWN = "↓"  

        # Choix par convention
        tile_size = 64

        width, height, map_data, next_map,switches,gates = self.read_map(file_path)
        max_x=tile_size * width
        max_y=tile_size * height


        self.camera_bounds = arcade.LRBT(
        WINDOW_WIDTH  / 2,
        max_x ,
        WINDOW_HEIGHT / 2,
        max_y  ,
        )

        
        self.next_map = next_map
    
        for switch_conf in switches:
            switch_pos = (switch_conf["x"], switch_conf["y"])
            self.switch_infos[switch_pos] = switch_conf
            print(f"Switch position: {switch_pos}, state: {switch_conf['state']}")
        
      
        self.gate_states = {}
        for gate_conf in gates:
            gate_pos = (gate_conf["x"], gate_conf["y"])
            is_open = (gate_conf.get("state", "closed") == "open")
            self.gate_states[gate_pos] = is_open 


        NO_LEFT_BOUNDS = width 
        NO_RIGHT_BOUNDS = 0
        NO_UP_BOUNDS = 0
        NO_DOWN_BOUNDS = height

        def bfs_connected_components(start_x: int, start_y: int) -> list[tuple[int, int]]:
            """Find connected components using BFS."""
            connected_components = []
            if  map_data[start_y][start_x]  in ASSETS and map_data[start_y][start_x] not in {"*","p", "S","|","^"}:
                # Initialize BFS
                queue = [(start_x, start_y)]
                visit = {(start_x, start_y)}
                while queue:
                    x, y = queue.pop(0)
                    connected_components.append((x, y))
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        new_x = x + dx
                        new_y = y + dy
                    # Correct bounds check
                        if  0 <= new_y < height and 0 <= new_x < width :
                            if (new_x, new_y) not in visit and map_data[new_y][new_x] in ASSETS and map_data[new_y][new_x] not in {"*","p", "S","|","^"}:
                                queue.append((new_x, new_y))
                                visit.add((new_x, new_y))
                        else :
                            continue
            return connected_components
        
        def calculate_platforms_bounds(connected_components: list[tuple[int, int]]) -> dict[Arrow, int]:
            """Calculate the bounds of the platforms."""

            NO_LEFT_BOUNDS = width 

            NO_RIGHT_BOUNDS = 0

            NO_UP_BOUNDS = 0

            NO_DOWN_BOUNDS = height 

            Bounds: dict[Arrow, int] = {
                    Arrow.LEFT: NO_LEFT_BOUNDS,
                    Arrow.RIGHT: NO_RIGHT_BOUNDS,
                    Arrow.UP: NO_UP_BOUNDS,
                    Arrow.DOWN: NO_DOWN_BOUNDS
                }
            for coordinates in connected_components:

                x,y = coordinates

                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:

                    new_x = x + dx

                    new_y = y + dy

                    if 0 <= new_y < height and 0 <= new_x < width:
                         
                         if map_data[new_y][new_x] == "←" and dx == -1:
                              
                              check_limit_l = new_x
                              
                              while check_limit_l>= 0 and map_data[new_y][check_limit_l] == "←" :
                                   
                                   Bounds[Arrow.LEFT] = min(Bounds[Arrow.LEFT], check_limit_l )
                                   
                                   check_limit_l -= 1
                         
                         
                         if map_data[new_y][new_x] == "→" and dx == 1:
                              
                              check_limit_r = new_x
                              
                              while check_limit_r< width and map_data[new_y][check_limit_r] == "→":
                                   
                                   Bounds[Arrow.RIGHT] = max(Bounds[Arrow.RIGHT], check_limit_r )

                                   check_limit_r +=1

                         
                         
                         if map_data[new_y][new_x] == "↑" and dy == 1:
                              
                              check_limit_u = new_y
                              
                              while check_limit_u < height and map_data[check_limit_u][new_x] == "↑":
                                   
                                   Bounds[Arrow.UP] = max(Bounds[Arrow.UP], check_limit_u )

                                   check_limit_u += 1
                         
                         
                         if map_data[new_y][new_x] == "↓" and dy == -1:
                              
                              check_limit_d = new_y
                              
                              while check_limit_d>= 0 and map_data[check_limit_d][new_x] == "↓":
                                   
                                   Bounds[Arrow.DOWN] = min(Bounds[Arrow.DOWN], check_limit_d )

                                   check_limit_d -= 1
            return Bounds 
        
        def calculate_platforms_borders(connected_components: list[tuple[int, int]]) -> tuple[int, int, int, int]:
            """Calculate the borders of the platforms."""
            left = min(x for x, y in connected_components)

            right = max(x for x, y in connected_components)

            up = max(y for x, y in connected_components)

            down = min(y for x, y in connected_components)

            return left, right, up, down
        
        visited = set()
        for y in range(len(map_data)):
            row=map_data[y]
            print("")  # Use actual map_data length, not height
            for x in range(len(row)):
                tile = row[x]
                print(tile,end=" ")

                if (x, y) in visited:
                    continue
                elif tile == "S" and (x, y) not in visited:
                    # Create the player sprite
                    self.player_sprite = arcade.Sprite(ASSETS[tile], center_x=GameView.coordinate(x, tile_size), center_y=GameView.coordinate(y, tile_size), scale=0.5)
                
                    self.player_sprite.center_x, self.player_sprite.center_y = GameView.coordinate(x, tile_size), GameView.coordinate(y, tile_size)
                
                    self.player_sprite_list.append(self.player_sprite) if self.player_sprite not in self.player_sprite_list else None
                
                    visited.add((x, y))
                elif tile == "*" and (x, y) not in visited:
                    # Create a coin sprite
                
                    coin = arcade.Sprite(ASSETS[tile], center_x=GameView.coordinate(x, tile_size), center_y=GameView.coordinate(y, tile_size), scale=0.5)
                
                    self.coin_list.append(coin) if coin not in self.coin_list else None
                
                    visited.add((x, y))

                elif tile == "p" and (x, y) not in visited:
                    #Create an apple sprite
                    powerup = arcade.Sprite(ASSETS[tile], center_x=GameView.coordinate(x, tile_size), center_y=GameView.coordinate(y, tile_size), scale=0.5)
                    self.powerup_list.append(powerup) if powerup not in self.powerup_list else None
                    visited.add((x, y))

                elif tile == "o" and (x, y) not in visited:
                    # Create an entity sprite
                    
                    blob = Blob(GameView.coordinate(x, tile_size), GameView.coordinate(y, tile_size), self)
                    
                    self.Entities.append(blob) if blob not in self.Entities else None
                    
                    visited.add((x, y))
                elif tile == "v" and (x, y) not in visited:
                    # Create an entity sprite
                        
                        bat = Bat(GameView.coordinate(x, tile_size), GameView.coordinate(y, tile_size), self)
                        
                        self.Entities.append(bat) if bat not in self.Entities else None
                        
                        visited.add((x, y))
                    
                
                elif tile == "G"  and (x, y) not in visited:
                    # Create an entity sprite
                        
                        ghost = Ghost(GameView.coordinate(x, tile_size), GameView.coordinate(y, tile_size), self)
                        
                        self.Entities.append(ghost) if ghost not in self.Entities else None
                        
                        visited.add((x, y))
                elif tile == "|" and (x, y) not in visited:
                    # Only spawn a gate if it is not open
                    is_open = self.gate_states.get((x, y), False)
                    if not is_open:
                        gate = arcade.Sprite(ASSETS[tile], center_x=GameView.coordinate(x, tile_size), center_y=GameView.coordinate(y, tile_size), scale=0.5)
                        self.gate_list.append(gate)
                        self.wall_list.append(gate)
                        visited.add((x, y))

                elif tile == "^" and (x,y) not in visited:
                    switch_data = self.switch_infos.get((x, y), None)
                    if switch_data is None:
                        raise ValueError(f"missing configuraion for switch at {(x, y)}")
                    switch_state = switch_data["state"]
                    sprite = ASSETS[tile] if switch_state == "off" else ":resources:/images/tiles/leverRight.png" 
                    switch = arcade.Sprite(sprite, center_x=GameView.coordinate(x, tile_size), center_y=GameView.coordinate(y, tile_size), scale=0.5)
                    self.switch_list.append(switch) if switch not in self.switch_list else None
                    self.sprite_to_switch_info[switch] = switch_data
                    visited.add((x, y))
                    
                


                elif tile in ASSETS and tile not in {"*","p", "S", "|","^"} and (x, y) not in visited:
                    Block = bfs_connected_components(x, y)
                    if Block:
                        Bounds = calculate_platforms_bounds(Block)
                
                        left_side, right_side, up_side, down_side = calculate_platforms_borders(Block)
                
                        # Create a platform sprite
                
                        if (Bounds[Arrow.LEFT] != NO_LEFT_BOUNDS or Bounds[Arrow.RIGHT] != NO_RIGHT_BOUNDS) and ( Bounds[Arrow.UP] != NO_UP_BOUNDS or Bounds[Arrow.DOWN] != NO_DOWN_BOUNDS):
                
                            raise ValueError("Invalid platform bounds: both horizontal and vertical bounds are set.")


                
                        if  Bounds[Arrow.LEFT] != NO_LEFT_BOUNDS or Bounds[Arrow.RIGHT] != NO_RIGHT_BOUNDS:
                
                            for coordinates in Block:
                
                                cx, cy = coordinates

                                tile = map_data[cy][cx]

                                if (cx, cy) not in visited:

                                    platform = arcade.Sprite(ASSETS[tile], center_x=GameView.coordinate(cx, tile_size), center_y=GameView.coordinate(cy, tile_size), scale=0.5)

                                    platform.change_x = -PLATFORM_MOVEMENT_SPEED_L

                                    platform.boundary_right = GameView.coordinate(cx, tile_size) + max(GameView.coordinate(Bounds[Arrow.RIGHT] + 0.5, tile_size) - GameView.coordinate(right_side, tile_size), 0)

                                    platform.boundary_left = GameView.coordinate(cx, tile_size) + min(GameView.coordinate(Bounds[Arrow.LEFT] - 0.5, tile_size) - GameView.coordinate(left_side, tile_size), 0)
                                


                                    self.platform_list.append(platform) if platform not in self.platform_list else None

                                    if tile == "£":

                                        self.lava_list.append(platform) if platform not in self.lava_list else None

                                    if tile == "E":

                                        self.exit_list.append(platform) if platform not in self.exit_list else None

                                    visited.add((cx, cy))



                        if Bounds[Arrow.UP] != NO_UP_BOUNDS or Bounds[Arrow.DOWN] != NO_DOWN_BOUNDS:

                            for coordinates in Block:
                                cx, cy = coordinates

                                tile = map_data[cy][cx]

                        
                                platform = arcade.Sprite(ASSETS[tile], center_x=GameView.coordinate(cx, tile_size), center_y=GameView.coordinate(cy, tile_size), scale=0.5)

                                platform.change_y = PLATFORM_MOVEMENT_SPEED_V
                                
                                platform.boundary_top = GameView.coordinate(cy, tile_size) + max(GameView.coordinate(Bounds[Arrow.UP] + 0.5, tile_size) - GameView.coordinate(up_side, tile_size), 0)
                                
                                platform.boundary_bottom = GameView.coordinate(cy, tile_size) + min(GameView.coordinate(Bounds[Arrow.DOWN] - 0.5, tile_size) - GameView.coordinate(down_side, tile_size), 0)
                                
                                self.platform_list.append(platform) if platform not in self.platform_list else None
                                
                                if tile == "£":

                                    self.lava_list.append(platform) if platform not in self.lava_list else None
                                
                                if tile == "E" :

                                    self.exit_list.append(platform) if platform not in self.exit_list else None

                                visited.add((cx, cy))

                        # Create a wall sprite
                        else :
                       
                            for coordinates in Block:
                       
                                cx,cy = coordinates
                       
                                tile = map_data[cy][cx]
                        
                       
                                if (cx, cy) not in visited:
                       
                                    if tile == "£":
                       
                                        lava = arcade.Sprite(ASSETS[tile], center_x=GameView.coordinate(cx, tile_size), center_y=GameView.coordinate(cy, tile_size), scale=0.5)
                       
                                        self.lava_list.append(lava) if lava not in self.lava_list else None

                                        visited.add((cx,cy))
                                    
                       
                                    elif tile == "E":
                       
                                        exit = arcade.Sprite(ASSETS[tile], center_x=GameView.coordinate(cx, tile_size), center_y=GameView.coordinate(cy, tile_size), scale=0.5)
                       
                                        self.exit_list.append(exit) if exit not in self.exit_list else None

                                        visited.add((cx, cy))
                                        
                                    else :
                       
                                        wall = arcade.Sprite(ASSETS[tile], center_x=GameView.coordinate(cx, tile_size), center_y=GameView.coordinate(cy, tile_size), scale=0.5)
                       
                                        self.wall_list.append(wall) if wall not in self.wall_list else None

                                        visited.add((cx, cy))


        print(f"{len(self.switch_list)} switches, {len(self.platform_list)} plateformes ")


        self.switch_platform: dict[arcade.Sprite, tuple[arcade.Sprite, float, float]] = {}
        for switch in self.switch_list:
            plats = arcade.get_sprites_at_point(
                (switch.center_x, switch.center_y - tile_size),
                self.platform_list
            )
            if plats:
                plat = plats[0]
                dx = switch.center_x - plat.center_x
                dy = switch.center_y - plat.center_y
                self.switch_platform[switch] = (plat, dx, dy)
        
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.wall_list,
            platforms=self.platform_list,  # Ensure moving platforms are included here
            gravity_constant=PLAYER_GRAVITY
        )
        self.physics_engine.disable_multi_jump()

        # Add a cooldown timer for sword-switch collision
        self._last_sword_switch_time = 0.0
    
    def switch_mvt(self) -> None:
        for switch_sprite, (platform_sprite, dx, dy) in self.switch_platform.items():
            if platform_sprite is None:
                continue
            switch_sprite.center_x = platform_sprite.center_x + dx
            switch_sprite.center_y = platform_sprite.center_y + dy

    def run_switch(self, switch: arcade.Sprite) -> None:
        switch_info = self.sprite_to_switch_info.get(switch)
        if not switch_info or not switch_info.get("enabled", False):
            return

        # Toggle the switch state
        current_state = switch_info["state"]
        new_state: Literal["on", "off"] = "off" if current_state == "on" else "on"
        switch_info["state"] = new_state

        # Update the lever sprite image based on the new state
        if new_state == "on":
            switch.texture = arcade.load_texture(":resources:/images/tiles/leverRight.png")
        else:
            switch.texture = arcade.load_texture(":resources:/images/tiles/leverLeft.png")

        actions = switch_info["switch_on"] if new_state == "on" else switch_info["switch_off"]

        # Run all actions for the current state (switch_on or switch_off)
        for action in actions:
            coord = (action["x"], action["y"])
            if action["action"] == "open-gate":
                self.gate_states[coord] = True
                for gate in list(self.gate_list):
                    if int(gate.center_x) == int(GameView.coordinate(coord[0])) and int(gate.center_y) == int(GameView.coordinate(coord[1])):
                        gate.remove_from_sprite_lists()
            if action["action"] == "close-gate":
                self.gate_states[coord] = False
                already_exists = any(
                    int(gate.center_x) == int(GameView.coordinate(coord[0])) and int(gate.center_y) == int(GameView.coordinate(coord[1]))
                    for gate in self.gate_list
                )
                if not already_exists:
                    gate_sprite = arcade.Sprite(ASSETS["|"], center_x=GameView.coordinate(coord[0]), center_y=GameView.coordinate(coord[1]), scale=0.5)
                    self.gate_list.append(gate_sprite)
                    self.wall_list.append(gate_sprite) if gate_sprite not in self.wall_list else None
            if action["action"] == "disable":
                switch_info["enabled"] = False

    def on_draw(self) -> None:
        """Render the screen."""
        self.clear() # always start with self.clear()
        with self.camera_score.activate():
            w, h = arcade.get_window().get_size()
            if self.game_over:
                arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
                self.clear()
                arcade.draw_text("GAME OVER", w / 2, h / 2 + 30,
                    arcade.color.RED, 50, anchor_x="center")
                arcade.draw_text("Press SPACE to play", w / 2, h / 2 - 30,
                    arcade.csscolor.WHITE, 24, anchor_x="center")
                
                for i, heart in enumerate(self.heart_list):
                    heart.alpha = 255 if i < self.lives else 100
                self.heart_list.draw()
                return 

        self.camera.use()
        self.Entities.draw()
        self.wall_list.draw()
        self.coin_list.draw()
        self.powerup_list.draw()
        self.player_sprite_list.draw()
        self.lava_list.draw()
        self.exit_list.draw()
        self.platform_list.draw()
        self.switch_list.draw()
        self.gate_list.draw()

        with self.camera_score.activate():
            arcade.draw_text(f"SCORE {self.score}",
                            self.window.width - 150,
                            self.window.height - 30,
                            arcade.csscolor.WHITE, 18)

            active = self.sword if self.active_weapon_index == 0 else self.bowArrow
            arcade.draw_texture_rect(
                texture=active.texture,
                rect=Rect(left=18, right=18+64,
                        bottom=18, top=18+64,
                        width=64, height=64,
                        x=40, y=self.window.height-30)
            )

            for i, heart in enumerate(self.heart_list):
                heart.alpha = 255 if i < self.lives else 100
            self.heart_list.draw()
            

    
    def check_for_gameover(self)-> None :

        if time.time() < self.hidden_time:
            return 
        
        touched_lava = any(lava.collides_with_point((self.player_sprite.center_x, self.player_sprite.bottom - 1)) for lava in self.lava_list)
        if touched_lava :
            arcade.play_sound(self.gameover_sound,loop=False)
            self.hidden_time = 0
            self.score = 0
            self.lives -= 1
            if self.lives <= 0:
                self.lives = 0
                self.game_over = True
                self.game_over_time = time.time()
            self.setup()

        if len(arcade.check_for_collision_with_list(self.player_sprite, self.Entities)) != 0 :
            arcade.play_sound(self.gameover_sound,loop=False)
            self.hidden_time = 0
            self.score = 0
            self.lives -= 1
            self.on_draw()
            if self.lives <= 0:
                self.lives = 0
                self.game_over = True
                self.game_over_time = time.time()
            self.setup()




    def update_player_speed(self)-> None :
        self.player_sprite.change_x = 0 
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = + PLAYER_MOVEMENT_SPEED
        if self.up_pressed and self.can_jump:
                arcade.play_sound(self.jump_sound,loop=False)
                self.player_sprite.change_y = + PLAYER_JUMP_SPEED
                self.can_jump = False 

    def on_key_press(self, key : int , modifiers :  int ) -> None :
        "Called when the user presses a key on the keyboard"

        if self.game_over and key == arcade.key.SPACE:
            self.lives = self.max_lives
            self.score = 0
            self.game_over = False
            self.setup()
            return

        match key :
            case arcade.key.RIGHT:
                #start moving to the right
                self.right_pressed = True
                self.update_player_speed()
            case arcade.key.LEFT :
                #start moving to the left 
                self.left_pressed = True
                self.update_player_speed()
            case arcade.key.UP :
                #jump by giving initial vertical speed
                self.up_pressed = True
                self.update_player_speed()
            case arcade.key.SPACE :
                #reset the game
                arcade.play_sound(self.gameover_sound,loop=False)
                self.score = 0
                self.setup("maps/map1.txt")

         

    def on_key_release(self, key : int , modifiers : int ) -> None :
        """Called when the user releases a key on the keyboard"""
        match key :
            case   arcade.key.RIGHT :
                #stop lateral movement
                self.right_pressed =  False
                self.update_player_speed()
            case arcade.key.LEFT :
                self.left_pressed = False
                self.update_player_speed()
            case arcade.key.UP :
                self.up_pressed = False 
                self.update_player_speed()


    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Handle mouse press events."""
        world_x, world_y, _ = self.camera.unproject((x, y))

        if button == arcade.MOUSE_BUTTON_RIGHT:
            # Switch weapon
            self.active_weapon_index = (self.active_weapon_index + 1) % 2
            self.active_weapon_sprite = self.weapon[self.active_weapon_index]

        active_weapon = self.weapon[self.active_weapon_index]

        if button == arcade.MOUSE_BUTTON_LEFT:
            if active_weapon == self.sword:
                # Calculate the angle of the sword towards the mouse position
                angle = 45 - math.degrees(math.atan2(world_y - self.player_sprite.center_y,
                                                     world_x - self.player_sprite.center_x))

                # Set the sword angle
                self.sword.angle = angle

                # Determine where to place the sword (either left or right of the player)
                if world_x >= self.player_sprite.center_x:
                    self.sword.center_x = self.player_sprite.right + 10
                else:
                    self.sword.center_x = self.player_sprite.left - 10

                # Adjust the vertical position slightly above or below the player
                self.sword.center_y = self.player_sprite.center_y

                # Add the sword to the sprite list to make it visible
                if self.sword not in self.player_sprite_list:
                    self.player_sprite_list.append(self.sword)

                self.sword_draw_time = time.time() # Record the time when the sword was drawn

            elif active_weapon == self.bowArrow:
                # Set the bowArrow's initial position and angle
                if x >= self.player_sprite.center_x:
                    self.bowArrow.center_x = self.player_sprite.right + 10
                else:
                    self.bowArrow.center_x = self.player_sprite.left - 10

                self.bowArrow.center_y = self.player_sprite.center_y

                # Calculate the angle of the bowArrow towards the mouse position
                bowArrow_angle = -math.degrees(math.atan2(y - self.player_sprite.center_y,
                                                          x - self.player_sprite.center_x))
                self.bowArrow.angle = bowArrow_angle

                # Add the bowArrow to the sprite list
                if self.bowArrow not in self.player_sprite_list:
                    self.player_sprite_list.append(self.bowArrow)

                # Store the target direction for the arrow
                self.arrow_target_x = world_x
                self.arrow_target_y = world_y

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Handle mouse release events."""
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.sword in self.player_sprite_list:
                self.player_sprite_list.remove(self.sword)

            if self.bowArrow in self.player_sprite_list:
                self.bowArrow.remove_from_sprite_lists()

                # Create a new arrow for each release
                new_arrow = arcade.Sprite(
                    WEAPON["arrow"],
                    scale=0.5 * 0.7,
                )

                # Set the arrow's initial position
                new_arrow.center_x = self.player_sprite.center_x
                new_arrow.center_y = self.player_sprite.center_y

                # Calculate the arrow's velocity based on the bowArrow's angle
                arrow_angle = -math.degrees(math.atan2(self.arrow_target_y - self.player_sprite.center_y,
                                                       self.arrow_target_x - self.player_sprite.center_x))
                new_arrow.angle = arrow_angle
                new_arrow.change_x = ARROW_SPEED * math.cos(math.radians(arrow_angle))
                new_arrow.change_y = -ARROW_SPEED * math.sin(math.radians(arrow_angle))

                # Add the new arrow to the sprite list
                self.player_sprite_list.append(new_arrow)

    def pan_camera_to_player(self, panning_fraction: float = 0.3) -> None:
        """Pan the camera to follow the player."""
        self.camera.position = arcade.math.smerp_2d(
            self.camera.position,
            self.player_sprite.position,
            self.window.delta_time,
            panning_fraction,
        )

        position = arcade.camera.grips.constrain_xy(
            self.camera.view_data,
            self.camera_bounds,
        )
        self.camera.position = arcade.Vec2(position[0], position[1])

    def on_update (self,delta_time : float ) -> None :
        """Called once per frame, before drawing.
        This is where in-world time "advances", or "ticks".
        """
        if self.game_over:
            return
        self.physics_engine.update()

        if self.physics_engine.can_jump() :
            self.can_jump = True

        self.pan_camera_to_player()

        if len(arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)) != 0:
            for coin in arcade.check_for_collision_with_list(self.player_sprite, self.coin_list):
                self.score += 1
                coin.remove_from_sprite_lists()
                arcade.play_sound(self.collect_coin_sound, loop=False)

        if len(arcade.check_for_collision_with_list(self.player_sprite, self.powerup_list)) != 0:
            for powerup in arcade.check_for_collision_with_list(self.player_sprite, self.powerup_list):
                self.hidden_time = time.time() + 8
                powerup.remove_from_sprite_lists()
                arcade.play_sound(self.collect_coin_sound, loop=False)

 
        if time.time() < self.hidden_time: #blinkblink
            if int(time.time() * 20) % 2 == 0: #change in 0.05s 
                if not self.blink_state:
                    self.player_sprite.alpha = 100
                    self.blink_state = True
            else:
                if self.blink_state:
                    self.player_sprite.alpha = 220
                    self.blink_state = False
        else:
            self.player_sprite.alpha = 255  
        
        self.sword.update()
        self.bowArrow.update()
        self.check_for_gameover()
        self.platform_list.update()

        self.switch_mvt()


        # Update entities
        for entities in self.Entities:
            entities.on_update(delta_time)
        if self.exit_list:
            if math.dist((self.player_sprite.center_x, self.player_sprite.center_y),( self.exit_list[0].center_x, self.exit_list[0].center_y)) <= 64 :
                arcade.play_sound(self.next_level, loop=False)
                self.setup(self.next_map)
            
        # Update all arrows in the sprite list
        arrows_to_remove: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()  # Track arrows to remove
        for arrow in self.player_sprite_list:
            if arrow != self.player_sprite and arrow != self.bowArrow and arrow != self.sword :
                if arrow.center_y > 0:
                    arrow.change_y -= ARROW_GRAVITY  # Apply gravity
                    # Check for collisions or if the arrow goes out of bounds
                    combined_spritelist: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
                    if arcade.check_for_collision_with_list(arrow, self.wall_list):
                        # If the arrow hits a wall, remove it
                        arrows_to_remove.append(arrow) if arrow not in arrows_to_remove else None
                    elif arcade.check_for_collision_with_list(arrow, self.lava_list):
                        # If the arrow hits lava, remove it
                        arrows_to_remove.append(arrow) if arrow not in arrows_to_remove else None
                    elif arcade.check_for_collision_with_list(arrow, self.exit_list):
                        # If the arrow hits the exit, remove it
                        arrows_to_remove.append(arrow) if arrow not in arrows_to_remove else None
                    elif arcade.check_for_collision_with_list(arrow, self.platform_list):
                        # If the arrow hits a platform, remove it
                        arrows_to_remove.append(arrow) if arrow not in arrows_to_remove else None
                    if arcade.check_for_collision_with_list(arrow, self.Entities):
                        # If the arrow hits an entity, remove it
                        hit_entity = arcade.check_for_collision_with_list(arrow, self.Entities)[0]
                        hit_entity.remove_from_sprite_lists()
                        arrows_to_remove.append(arrow) if arrow not in arrows_to_remove else None
                    if arcade.check_for_collision_with_list(arrow, self.switch_list):
                        # If the arrow hits a switch, run the switch
                        hit_switch = arcade.check_for_collision_with_list(arrow, self.switch_list)[0]
                        self.run_switch(hit_switch)
                        arrows_to_remove.append(arrow) if arrow not in arrows_to_remove else None
                else:
                    arrows_to_remove.append(arrow)
                arrow.update()
                

        # Remove arrows marked for deletion
        if arrows_to_remove:
            for arrow in arrows_to_remove:
                arrow.remove_from_sprite_lists()
        
        # Make the sword follow the player
        if self.sword in self.player_sprite_list:
            self.sword.change_x = self.player_sprite.change_x
            self.sword.change_y = self.player_sprite.change_y

        # Check for collisions with the sword
        if self.sword_draw_time is not None:
            time_since_drawn = time.time() - self.sword_draw_time
            if time_since_drawn <= 0.2:
                hit_with_sword = arcade.check_for_collision_with_list(self.sword, self.Entities)
                for monster in hit_with_sword:
                    monster.remove_from_sprite_lists()
                # Add cooldown for sword-switch collision
                now = time.time()
                if now - self._last_sword_switch_time > 0.25:
                    hit_sword_switch = arcade.check_for_collision_with_list(self.sword, self.switch_list)
                    for switch in hit_sword_switch:
                        self.run_switch(switch)
                    self._last_sword_switch_time = now


        