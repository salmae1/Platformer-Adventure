
from __future__ import annotations
from typing import Final
import arcade
import math
from Entity import Entity ,Blob , Bat


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
PLAYER_MOVEMENT_SPEED = 5
"""Lateral speed of the player, in pixels per frame."""
PLAYER_GRAVITY = 1
"""Gravity applied to the player, in pixels per frame²."""
PLAYER_JUMP_SPEED = 18
"""Instant vertical speed for jumping, in pixels per frame."""
class GameView(arcade.View):
    """Main in-game view."""
    player_sprite: arcade.Sprite
    Entities: arcade.SpriteList[Entity]
    player_sprite_list : arcade.SpriteList[arcade.Sprite]
    wall_list : arcade.SpriteList(use_spatial_hash=True) # type: ignore
    no_go_list :arcade.SpriteList(use_spatial_hash=True) #type: ignore
    """nogo is fixed """
    physics_engine : arcade.PhysicsEnginePlatformer
    camera : arcade.camera.Camera2D
    coin_list : arcade.SpriteList(use_spatial_hash=True)  # type: ignore


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

        self.camera = arcade.camera.Camera2D()
        self.camera_bounds = arcade.LRBT(
            WINDOW_WIDTH / 2.0,
            WINDOW_WIDTH ,
            WINDOW_HEIGHT / 2 ,
            WINDOW_HEIGHT
        )


    def setup(self) -> None:
        """Set up the game here."""
        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            center_x=400,
            center_y=465 ,
            scale = 0.5
        )
        self.sword = arcade.Sprite(
            "assets/kenney-voxel-items-png/sword_silver.png",
            scale=0.5 * 0.7,
        )

        self.blob  = Blob(
            center_x = 300 ,
            center_y = 465 ,
            game_view= self
        )
        self.bat = Bat(
            center_x = 200 ,
            center_y= 200 ,
            game_view= self  
        )
        self.wall_list = arcade.SpriteList()
        for i in range (0,1280,64):
            self.wall_sprite=arcade.Sprite(
                ":resources:images/tiles/grassMid.png",
                center_x= i ,
                center_y= 32 ,
                scale= 0.5
            )
            self.wall_list.append(self.wall_sprite)

        for i in range (280,800,64):
            self.wall_sprite=arcade.Sprite(
                ":resources:images/tiles/grassMid.png",
                center_x= i ,
                center_y= 400 ,
                scale= 0.5
            )
            self.wall_list.append(self.wall_sprite)

        self.no_go_list = arcade.SpriteList()
        for i in range (1280,2000,64):
            self.lava_sprite=arcade.Sprite(
                ":resources:images/tiles/lava.png",
                center_x= i ,
                center_y= 32 ,
                scale= 0.5
            )
            self.no_go_list.append(self.lava_sprite)    

        for i in range(256,1024,256) :
            wall_sprite=arcade.Sprite(
                ":resources:images/tiles/boxCrate_double.png",
                center_x= i ,
                center_y= 96,
                scale= 0.5
            )

            self.wall_list.append(wall_sprite)
            self.coin_list = arcade.SpriteList()

        for i in range(128,1250,256) :
                coin_sprite=arcade.Sprite(
                ":resources:images/items/coinGold.png",
                center_x= i ,
                center_y= 96,
                scale= 0.5
            )
                self.coin_list.append(coin_sprite)

        self.player_sprite_list =  arcade.SpriteList()
        self.player_sprite_list.append(self.player_sprite)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite ,
            walls = self.wall_list ,
            gravity_constant= PLAYER_GRAVITY
        )
        self.Entities = arcade.SpriteList()
        self.Entities.append(self.blob)
        self.Entities.append(self.bat)
               
                 


    def on_draw(self) -> None:
        """Render the screen."""
        self.clear() # always start with self.clear()
        self.camera.use()
        self.wall_list.draw()
        self.player_sprite_list.draw()
        self.coin_list.draw()
        self.no_go_list.draw()
        self.Entities.draw()
    
    def check_for_gameover(self)-> None :
        if len(arcade.check_for_collision_with_list(self.player_sprite, self.no_go_list)) != 0 :
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


    def on_mouse_press(self, x, y, button, modifiers):
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



    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT :
            self.player_sprite_list.pop(1)


    def pan_camera_to_player(self, panning_fraction : float = 0.2):
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
        self.blob.on_update()
        self.bat.on_update()
        
