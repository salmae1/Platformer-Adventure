from __future__ import annotations
from typing import Final
import arcade
import math
from Entity import Entity ,Blob , Bat
from arcade.types import Rect


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

PLAYER_MOVEMENT_SPEED = 5
"""Lateral speed of the player, in pixels per frame."""
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
    "£": ":resources:/images/tiles/lava.png",
    "S": ":resources:/images/animated_characters/female_person/femalePerson_idle.png",
    "E": ":resources:/images/tiles/signExit.png"
}
WEAPON = {
    "sword" : "assets/kenney-voxel-items-png/sword_bronze.png",
    "bow" : "assets/kenney-voxel-items-png/bow.png",
    "arrow" : "assets/kenney-voxel-items-png/arrow.png",
    "bowArrow" : "assets/kenney-voxel-items-png/bowArrow.png"
}



class GameView(arcade.View):
    """Main in-game view."""
    player_sprite: arcade.Sprite
    Entities: arcade.SpriteList[Entity]
    player_sprite_list : arcade.SpriteList[arcade.Sprite]
    wall_list : arcade.SpriteList(use_spatial_hash=True) # type: ignore
    physics_engine : arcade.PhysicsEnginePlatformer
    camera : arcade.camera.Camera2D
    camera_score : arcade.camera.Camera2D
    coin_list : arcade.SpriteList(use_spatial_hash=True)  # type: ignore


    def __init__(self) -> None:
        # Magical incantion: initialize the Arcade view
        super().__init__()

        # Choose a nice comfy background color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE
        self.score = 0

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


        self.camera = arcade.camera.Camera2D()
        self.camera_score = arcade.camera.Camera2D()
        self.camera_bounds = arcade.LRBT(
            WINDOW_WIDTH / 2.0,
            WINDOW_WIDTH ,
            WINDOW_HEIGHT / 2 ,
            WINDOW_HEIGHT
        )


    def read_map(self, file_path: str)-> tuple[int, int, list[str], str]:
        """read and analyse the map."""
    
        with open(file_path, 'r', encoding="utf-8", newline='') as f:
            lines = f.readlines()
        

        width = height = 0
        next_map =" "
        index = 0

        # Configuration
        while index < len(lines) and lines[index].strip()!= "---":
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
        while index < len(lines) and lines[index].strip() != "---":
            map_data.append(lines[index].rstrip("\n"))
            index += 1
        

        return width, height, map_data, next_map
    


    def setup( self, file_path: str = "maps/map1.txt") -> None:
        """Set up the game here."""

        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            center_x=400,
            center_y=465 ,
            scale = 0.5
        )
        
        self.sword = arcade.Sprite(
            WEAPON["sword"],
            scale=0.5 * 0.7,
        )
        self.bow = arcade.Sprite(
            WEAPON["bow"],
            scale=0.5 * 0.7,
        )
        self.arrow = arcade.Sprite(
            WEAPON["arrow"],
            scale=0.5 * 0.7,
        )
        self.bowArrow = arcade.Sprite(
            WEAPON["bowArrow"],
            scale=0.5 * 0.7,
        )
        self.weapon = [self.sword, self.bow]
        self.active_weapon_index = 1
        self.active_weapon_sprite = self.bow

        self.player_sprite_list= arcade.SpriteList()
        self.player_sprite_list.append(self.player_sprite)
        self.wall_list = arcade.SpriteList(use_spatial_hash = True)
        self.coin_list = arcade.SpriteList(use_spatial_hash = True)
        self.lava_list : arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash = True)
        self.exit_list : arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash = True)
        self.Entities = arcade.SpriteList()

        # Choix par convention
        tile_size = 64

        width, height, map_data, next_map = self.read_map(file_path)

        for y, row in enumerate(reversed(map_data)):
            for x, char in enumerate(row.ljust(width)):
                map_x = x * tile_size +tile_size//2
                map_y = y * tile_size +tile_size//2

                if char == "=":
                    grass = arcade.Sprite(ASSETS["="], scale=0.5)
                    grass.center_x = map_x
                    grass.center_y = map_y
                    self.wall_list.append(grass)
                elif char == "-":
                    grassH = arcade.Sprite(ASSETS["-"], scale=0.5)
                    grassH.center_x = map_x
                    grassH.center_y = map_y
                    self.wall_list.append(grassH)
                elif char == "x":
                    box = arcade.Sprite(ASSETS["x"], scale=0.5)
                    box.center_x = map_x
                    box.center_y = map_y
                    self.wall_list.append(box)
                elif char == "*":
                    coin = arcade.Sprite(ASSETS["*"], scale=0.5)
                    coin.center_x = map_x
                    coin.center_y = map_y
                    self.coin_list.append(coin)
                elif char == 'S':
                    self.player_sprite.center_x = map_x
                    self.player_sprite.center_y = map_y       
                elif char == "£":
                    lava = arcade.Sprite(ASSETS["£"], scale = 0.5)
                    lava.center_x = map_x
                    lava.center_y = map_y
                    self.lava_list.append(lava)
                elif char == "E":
                    exit = arcade.Sprite(ASSETS["E"], scale= 0.5)
                    exit.center_x = map_x
                    exit.center_y = map_y
                    self.exit_list.append(exit)
                elif char == "o":
                    exit= Blob(map_x,map_y,game_view= self)
                    self.Entities.append(exit)
                elif char ==  "v":
                    exit = Bat(map_x,map_y,self)
                    self.Entities.append(exit)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.wall_list,
            gravity_constant=PLAYER_GRAVITY
        )


    
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
                self.score = 0

         

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


    def on_mouse_press(self, x : int , y : int, button : int, modifiers : int) -> None:

        if button == arcade.MOUSE_BUTTON_RIGHT:
            #Switch weapon
            self.active_weapon_index = (self.active_weapon_index +1) % 2
            self.active_weapon_sprite = self.weapon[self.active_weapon_index]

        active_weapon = self.weapon[self.active_weapon_index]

        if button == arcade.MOUSE_BUTTON_LEFT:
            self.weapon_visible = True
            # Convert screen coordinates to world coordinates
            world_x, world_y = (x - (WINDOW_WIDTH / 2)) / self.camera.zoom + self.camera.position[0] ,(y - (WINDOW_HEIGHT / 2)) / self.camera.zoom + self.camera.position[1]

            # Calculate the angle of the sword towards the mouse position
            angle = 45-math.degrees(math.atan2(world_y - self.player_sprite.center_y,
                                          world_x - self.player_sprite.center_x))

            # Set the sword angle
            self.active_weapon_sprite.angle = angle

        # Determine where to place the sword (either left or right of the player)
            if world_x >= self.player_sprite.center_x:
                active_weapon.center_x = self.player_sprite.right + 10
            else:
                active_weapon.center_x = self.player_sprite.left - 10

            # Adjust the vertical position slightly above or below the player
            active_weapon.center_y = self.player_sprite.center_y

            # Add the sword to the sprite list to make it visible
            self.player_sprite_list.append(active_weapon)

            if active_weapon == self.bow:
                self.arrow.center_x = self.player_sprite.center_x
                self.arrow.center_y = self.player_sprite.center_x

                arrow_angle = 45-math.degrees(math.atan2(world_y - self.player_sprite.center_y,
                                          world_x - self.player_sprite.center_x))
                self.arrow.angle = angle
                self.arrow.change_x = ARROW_SPEED * math.cos(math.radians(arrow_angle))
                self.arrow.change_y = ARROW_SPEED * math.sin(math.radians(arrow_angle))
                self.player_sprite_list.append(self.arrow)

        
    def kill_monster(self) -> None :
        hit_with_sword = arcade.check_for_collision_with_list(self.sword,self.Entities)
        hit_with_arrow = arcade.check_for_collision_with_list(self.arrow,self.Entities)
        if hit_with_sword :
            monster = hit_with_sword[0]
            monster.remove_from_sprite_lists()
        if hit_with_arrow :
            monster = hit_with_arrow[0]
            monster.remove_from_sprite_lists()



    def on_mouse_release(self, x : int , y : int, button : int , modifiers : int)-> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.active_weapon_index == 0:
                self.sword.remove_from_sprite_lists()
            else:
                self.bow.remove_from_sprite_lists()
                self.arrow.remove_from_sprite_lists()
        
    
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

        with self.camera_score.activate():
            w, h = arcade.get_window().get_size()
            SCORE_TEXT = f"SCORE {self.score}"
            arcade.draw_text(SCORE_TEXT, w - 110, h - 30, 
                             arcade.csscolor.WHITE, 18)
            if self.active_weapon_index == 0:
                active_weapon_image = self.sword
            else:
                active_weapon_image = self.bowArrow
            weapon_rect = Rect( left=18, right=18+64, 
                               bottom=18, top=18+64, 
                               width=64, height=64,
                               x=40, y=h-30)
            arcade.draw_texture_rect(
                texture=active_weapon_image.texture,
                rect=weapon_rect
            )


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
            self.score += 1

        self.sword.update()
        self.bow.update()
        self.arrow.update()
        self.check_for_gameover()
        for entities in self.Entities:
            entities.on_update(delta_time)
        if arcade.check_for_collision_with_list(self.player_sprite, self.exit_list):
            arcade.play_sound(self.next_level, loop=False)
            self.setup("maps/map2.txt")
        
        if self.active_weapon_sprite:
            self.active_weapon_sprite.center_x = self.player_sprite.right + 10
            self.active_weapon_sprite.center_y = self.player_sprite.center_y


        for arrow in self.player_sprite_list:
            if isinstance(arrow, arcade.Sprite) and arrow != self.player_sprite:
                arrow.change_y -= ARROW_GRAVITY
                arrow.update

                if arcade.check_for_collision_with_list(arrow, self.lava_list) or arrow.bottom < 0:
                    arrow.remove_from_sprite_lists()

        

        







