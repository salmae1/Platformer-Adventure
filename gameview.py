from __future__ import annotations
from typing import Final
import arcade
import math
from Entity import Entity ,Blob , Bat
from enum import Enum

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
ASSETS = {
    "=": ":resources:/images/tiles/grassMid.png",
    "-": ":resources:/images/tiles/grassHalf_mid.png",
    "x": ":resources:/images/tiles/boxCrate_double.png",
    "*": ":resources:/images/items/coinGold.png",
    "£": ":resources:/images/tiles/lava.png",
    "S": ":resources:/images/animated_characters/female_person/femalePerson_idle.png",
    "E": ":resources:/images/tiles/signExit.png"
}
class GameView(arcade.View):
    """Main in-game view."""
    player_sprite: arcade.Sprite
    Entities: arcade.SpriteList[Entity]
    player_sprite_list : arcade.SpriteList[arcade.Sprite]
    wall_list: arcade.SpriteList [arcade.Sprite]
    physics_engine : arcade.PhysicsEnginePlatformer
    camera : arcade.camera.Camera2D
    coin_list : arcade.SpriteList[arcade.Sprite]
    lava_list : arcade.SpriteList[arcade.Sprite]
    exit_list : arcade.SpriteList[arcade.Sprite]   
    platform_list : arcade.SpriteList[arcade.Sprite]



    def __init__(self) -> None:
        # Magical incantion: initialize the Arcade view
        super().__init__()

        # Choose a nice comfy background color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        # Setup our game
        self.setup()
        #Track the current state of what key is pressed 
        self.left_pressed = False 
        self.right_pressed = False
        self.up_pressed = False
        self.can_jump = True
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav", streaming=False)
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav", streaming= False)
        self.gameover_sound = arcade.load_sound(":resources:sounds/gameover1.wav.", streaming = False)
        self.next_level = arcade.load_sound(":resources:/sounds/upgrade1.wav", streaming= False)
 

        self.camera = arcade.camera.Camera2D()
        self.camera_bounds = arcade.LRBT(
            WINDOW_WIDTH / 2.0,
            WINDOW_WIDTH ,
            WINDOW_HEIGHT / 2 ,
            WINDOW_HEIGHT
        )
    @staticmethod
    def read_map(file_path: str) -> tuple[int, int, list[str], str]:
        """read and analyse the map."""
    
        with open(file_path, 'r', encoding="utf-8", newline='\n') as f:
            lines = f.readlines()
        

        width = height = 0
        next_map = " "
        index = 0

        # Configuration
        while index < len(lines) and lines[index].strip() != "---":
            key, value = lines[index].strip().split(": ")
            if key == "width":
                width = int(value)
            elif key == "height":
                height = int(value)
            elif key == "next_map":
                next_map = str(value)
            index += 1
        

        index += 1
        map_data = []

        # Characters
        while index < len(lines)  and lines[index].rstrip() != "---":
            lines[index] = lines[index].rstrip().ljust(width)
            map_data.append(lines[index])
            index += 1
        
        map_data = list(reversed(map_data))
        return width, height, map_data, next_map
    


    def setup(self, file_path: str = "maps/map1.txt") -> None:
        """Set up the game here."""

        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            center_x=400,
            center_y=465,
            scale=0.5
        )

        self.sword = arcade.Sprite(
            "assets/kenney-voxel-items-png/sword_silver.png",
            scale=0.5 * 0.7,
        )
        self.player_sprite_list = arcade.SpriteList()
        self.player_sprite_list.append(self.player_sprite)
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList(use_spatial_hash=True)
        self.lava_list = arcade.SpriteList(use_spatial_hash=True)
        self.exit_list = arcade.SpriteList(use_spatial_hash=True)
        self.Entities = arcade.SpriteList()
        self.platform_list = arcade.SpriteList()
        class Arrow(Enum):
            LEFT = "←"
            RIGHT = "→"
            UP = "↑"
            DOWN = "↓"  

        # Choix par convention
        tile_size = 64

        width, height, map_data, next_map = self.read_map(file_path)
        NO_LEFT_BOUNDS = width 
        NO_RIGHT_BOUNDS = 0
        NO_UP_BOUNDS = 0
        NO_DOWN_BOUNDS = height

        def bfs_connected_components(start_x: int, start_y: int) -> list[tuple[int, int]]:
            """Find connected components using BFS."""
            connected_components = []
            if  map_data[start_y][start_x]  in ASSETS and map_data[start_y][start_x] not in {"*", "S"}:
                # Initialize BFS
                queue = [(start_x, start_y)]
                visited = {(start_x, start_y)}
                while queue:
                    x, y = queue.pop(0)
                    connected_components.append((x, y))
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        new_x = x + dx
                        new_y = y + dy
                    # Correct bounds check
                        if  0 <= new_y < height and 0 <= new_x < width :
                            if (new_x, new_y) not in visited and map_data[new_y][new_x] in ASSETS and map_data[new_y][new_x] not in {"*", "S"}:
                                queue.append((new_x, new_y))
                                visited.add((new_x, new_y))
                        else :
                            continue
            return connected_components
        
        def calculate_platforms_bounds (connected_components: list[tuple[int, int]]) -> dict[Arrow, int]:
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
        
        def calculate_platforms_borders (connected_components: list[tuple[int, int]]) -> tuple[int, int, int, int]:
            """Calculate the borders of the platforms."""
            left = min(x for x, y in connected_components)
            right = max(x for x, y in connected_components)
            up = max(y for x, y in connected_components)
            down = min(y for x, y in connected_components)
            return left, right, up, down
        
        def coordinate(x: int) -> int:
            """Convert tile coordinates to pixel coordinates."""
            return x * tile_size + tile_size // 2 
        
        visited = set()
        ## Loop through the map data and create the appropriate sprites
        import time 
        start_time = time.time()
        for  y in range(height):
            for x in range(width):
                
                tile = map_data[y][x]
                
                if tile == "S"  and (x,y) not in visited:
                    # Create the player sprite
                
                    self.player_sprite.center_x, self.player_sprite.center_y = coordinate(x),coordinate(y)
                
                    self.player_sprite_list.append(self.player_sprite) if self.player_sprite not in self.player_sprite_list else None
                
                    visited.add((x, y))
                
                    continue
                
                if tile == "*"  and (x,y) not in visited:
                
                    # Create a coin sprite
                
                    coin = arcade.Sprite(ASSETS[tile], center_x=coordinate(x), center_y=coordinate(y),scale=0.5)
                
                    self.coin_list.append(coin) if coin not in self.coin_list else None
                
                    visited.add((x, y))
                
                    continue

                if tile == "o" and (x,y) not in visited:
                    
                        # Create an entity sprite
                    
                        blob = Blob(coordinate(x), coordinate(y),self)
                    
                        self.Entities.append(blob) if blob not in self.Entities else None
                    
                        visited.add((x, y))
                    
                        continue
                
                if tile =="v" and (x,y) not in visited:
                        
                            # Create an entity sprite
                        
                            bat = Bat(coordinate(x), coordinate(y),self)
                        
                            self.Entities.append(bat) if bat not in self.Entities else None
                        
                            visited.add((x, y))
                        
                            continue
                
                
                if tile in ASSETS and tile not in {"*", "S"}:
                
                    Block = bfs_connected_components(x, y)
                
                    if Block:
                
                        Bounds= calculate_platforms_bounds(Block)
                
                        left_side, right_side, up_side, down_side = calculate_platforms_borders(Block)
                
                        # Create a platform sprite
                
                        if (Bounds[Arrow.LEFT] != NO_LEFT_BOUNDS or Bounds[Arrow.RIGHT] != NO_RIGHT_BOUNDS) and ( Bounds[Arrow.UP] != NO_UP_BOUNDS or Bounds[Arrow.DOWN] != NO_DOWN_BOUNDS):
                
                            raise ValueError("Invalid platform bounds: both horizontal and vertical bounds are set.")


                
                        if  Bounds[Arrow.LEFT] != NO_LEFT_BOUNDS or Bounds[Arrow.RIGHT] != NO_RIGHT_BOUNDS:
                
                            for coordinates in Block:
                
                                x, y = coordinates

                                tile = map_data[y][x]

                                if (x,y) not in visited:

                                    platform = arcade.Sprite(ASSETS[tile], center_x=coordinate(x), center_y=coordinate(y),scale=0.5)

                                    platform.change_x = PLATFORM_MOVEMENT_SPEED_L

                                    platform.boundary_right = coordinate(x) + max(coordinate(Bounds[Arrow.RIGHT])-coordinate(right_side),0)

                                    platform.boundary_left = coordinate(x) + min(-coordinate(left_side) + coordinate(Bounds[Arrow.LEFT]),0)

                                    self.platform_list.append(platform) if platform not in self.platform_list else None

                                    if tile == "£":

                                        lava = arcade.Sprite(ASSETS[tile], center_x=coordinate(x), center_y=coordinate(y),scale=0.5)

                                        self.lava_list.append(lava) if lava not in self.lava_list else None
                                    if tile == "E":

                                        exit = arcade.Sprite(ASSETS[tile], center_x=coordinate(x), center_y=coordinate(y),scale=0.5)

                                        self.exit_list.append(exit) if exit not in self.exit_list else None

                                    visited.add((x, y))



                        if Bounds[Arrow.UP] != NO_UP_BOUNDS or Bounds[Arrow.DOWN] != NO_DOWN_BOUNDS:

                            for coordinates in Block:

                                x, y = coordinates

                                tile = map_data[y][x]

                                if (x,y) not in visited:

                                    # Create a platform sprite

                                    platform = arcade.Sprite(ASSETS[tile], center_x=coordinate(x), center_y=coordinate(y),scale=0.5)

                                    platform.change_y = PLATFORM_MOVEMENT_SPEED_V
                                    
                                    platform.boundary_top= coordinate(y) + max(coordinate(Bounds[Arrow.UP])-coordinate(up_side),0)
                                    
                                    platform.boundary_bottom = coordinate(y) + min(coordinate(Bounds[Arrow.DOWN])-coordinate(down_side),0)
                                    
                                    self.platform_list.append(platform) if platform not in self.platform_list else None
                                    
                                    
                                    
                                    if tile == "£":
                                    
                                        lava = arcade.Sprite(ASSETS[tile], center_x=coordinate(x), center_y=coordinate(y),scale=0.5)
                                    
                                        self.lava_list.append(lava) if lava not in self.lava_list else None
                                    
                                    if tile == "E":
                                    
                                        exit = arcade.Sprite(ASSETS[tile], center_x=coordinate(x), center_y=coordinate(y),scale=0.5)
                                    
                                        self.exit_list.append(exit) if exit not in self.exit_list else None
                                    
                                    visited.add((x, y))

                        # Create a wall sprite
                        else :
                       
                            for coordinates in Block:
                       
                                x, y = coordinates
                       
                                tile = map_data[y][x]
                       
                                if (x,y) not in visited:
                       
                                    if tile == "£":
                       
                                        lava = arcade.Sprite(ASSETS[tile], center_x=coordinate(x), center_y=coordinate(y),scale=0.5)
                       
                                        self.lava_list.append(lava) if lava not in self.lava_list else None
                                        continue
                       
                                    if tile == "E":
                       
                                        exit = arcade.Sprite(ASSETS[tile], center_x=coordinate(x), center_y=coordinate(y),scale=0.5)
                       
                                        self.exit_list.append(exit) if exit not in self.exit_list else None
                                        continue
                       
                                    else :
                       
                                        wall = arcade.Sprite(ASSETS[tile], center_x=coordinate(x), center_y=coordinate(y),scale=0.5)
                       
                                        self.wall_list.append(wall) if wall not in self.wall_list else None
                                    visited.add((x, y))


        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.wall_list,
            platforms=self.platform_list,  # Ensure moving platforms are included here
            gravity_constant=PLAYER_GRAVITY
        )

    def on_draw(self) -> None:
        """Render the screen."""
        self.clear() # always start with self.clear()
        self.camera.use()
        self.Entities.draw()
        self.wall_list.draw()
        self.coin_list.draw()
        self.player_sprite_list.draw()
        self.lava_list.draw()
        self.Entities.draw_hit_boxes()
        self.platform_list.draw()
    
    def check_for_gameover(self)-> None :
        if len(arcade.check_for_collision_with_list(self.player_sprite, self.lava_list)) != 0 :
            arcade.play_sound(self.gameover_sound,loop=False)
            self.setup()
        if len(arcade.check_for_collision_with_list(self.player_sprite, self.Entities)) != 0 :
            arcade.play_sound(self.gameover_sound,loop=False)
            self.setup()

    def update_player_speed(self)-> None :
        self.player_sprite.change_x = 0 
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = + PLAYER_MOVEMENT_SPEED
        if self.up_pressed and self.can_jump:
            if self.player_sprite.change_y  == 0 :
                self.player_sprite.change_y = + PLAYER_JUMP_SPEED
                self.can_jump = False 

    def on_key_press(self, key : int , modifiers :  int ) -> None :
        "Called when the user presses a key on the keyboard"
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
                self.setup()

         

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


    def on_mouse_press(self, x : int , y : int, button : int, modifiers : int )-> None :
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Convert screen coordinates to world coordinates
            world_x, world_y = (x - (WINDOW_WIDTH / 2)) / self.camera.zoom + self.camera.position[0] ,(y - (WINDOW_HEIGHT / 2)) / self.camera.zoom + self.camera.position[1]

            # Calculate the angle of the sword towards the mouse position
            angle = 45-math.degrees(math.atan2(world_y - self.player_sprite.center_y,
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
            self.player_sprite_list.append(self.sword)
        
    def kill_monster(self) -> None :
        hit_with_sword = arcade.check_for_collision_with_list(self.sword,self.Entities)
        if hit_with_sword :
            monster = hit_with_sword[0]
            monster.remove_from_sprite_lists()



    def on_mouse_release(self, x : int , y : int, button : int , modifiers : int)-> None:
        if button == arcade.MOUSE_BUTTON_LEFT :
            self.sword.remove_from_sprite_lists()


    def pan_camera_to_player(self, panning_fraction : float = 0.2)->None:
        self.camera.position = arcade.math.smerp_2d(
            self.camera.position ,
            self.player_sprite.position ,
            self.window.delta_time ,
            panning_fraction
        )
        self.bounds = arcade.camera.grips.constrain_xy(
            self.camera.view_data ,
            self.camera_bounds ,
        )
        self.camera.position = arcade.Vec2(self.bounds[0],self.bounds[1])

    def on_update (self,delta_time : float ) -> None :
        """Called once per frame, before drawing.
        This is where in-world time "advances", or "ticks".
        """
        self.physics_engine.update()

        if self.physics_engine.can_jump() :
            self.can_jump = True

        self.pan_camera_to_player()

        self.kill_monster()
        if len(arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)) != 0:
            coin = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)[0]
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound, loop=False)
        self.sword.update()
        self.check_for_gameover()
        # Update entities
        for entities in self.Entities:
            entities.on_update(delta_time)
        if arcade.check_for_collision_with_list(self.player_sprite, self.exit_list):
            arcade.play_sound(self.next_level, loop=False)
            self.setup("maps/map2.txt")


