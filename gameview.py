import arcade


PLAYER_MOVEMENT_SPEED = 5
"""Lateral speed of the player, in pixels per frame."""
PLAYER_GRAVITY = 1
"""Gravity applied to the player, in pixels per frame²."""
PLAYER_JUMP_SPEED = 18
"""Instant vertical speed for jumping, in pixels per frame."""
ASSETS = {
    "=": ":resources:/images/tiles/grassMid.png",
    "-": ":resources:/images/tiles/grassHalf_mid.png",
    "x": ":resources:/images/tiles/boxCrate_double.png",
    "*": ":resources:/images/items/coinGold.png",
    "o": ":resources:/images/enemies/slimeBlue.png",
    "£": ":resources:/images/tiles/lava.png",
    "S": ":resources:/images/animated_characters/female_person/femalePerson_idle.png",
    "E": ":resources:/images/tiles/signExit.png"
}




class GameView(arcade.View):
    """Main in-game view."""


    player_sprite: arcade.Sprite
    player_sprite_list: arcade.SpriteList[arcade.Sprite]
    wall_list: arcade.SpriteList[arcade.Sprite]

    physics_engine: arcade.PhysicsEnginePlatformer

    camera : arcade.camera.Camera2D
    camera_score : arcade.camera.Camera2D


    def __init__(self) -> None:
        # Magical incantion: initialize the Arcade view
        super().__init__()

        # Choose a nice comfy background color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        self.score = 0



        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav", streaming=False)
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav", streaming= False)
        self.game_over_sound = arcade.load_sound(" :resources:sounds/gameover1.wav", streaming = False)
        self.next_level = arcade.load_sound(":resources:/sounds/upgrade1.wav", streaming= False)


        # Setup our game
        self.setup()



    def read_map(self, file_path):
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
    

        


    def setup(self, file_path = "maps/map1.txt" ) -> None:
        """Set up the game here."""
        self.wall_list = arcade.SpriteList(use_spatial_hash = True)
        self.coin_list = arcade.SpriteList(use_spatial_hash = True)
        self.lava_list = arcade.SpriteList(use_spatial_hash = True)
        self.exit_list = arcade.SpriteList(use_spatial_hash = True)

        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            center_x=64,
            center_y=128
            )
        self.player_sprite_list = arcade.SpriteList()
        self.player_sprite_list.append(self.player_sprite)


        width, height, map_data, next_map = self.read_map(file_path)


        # Choix par convention
        tile_size = 64

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


        
        

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.wall_list,
            gravity_constant=PLAYER_GRAVITY
        )

        self.camera = arcade.camera.Camera2D()
        self.camera_score = arcade.camera.Camera2D()



        


    def on_update(self, delta_time: float) -> None:
        """Called once per frame, before drawing.

        This is where in-world time "advances", or "ticks".
        """
        self.physics_engine.update()

        #waiting for a new version of mypy
        self.camera.position = self.player_sprite.position #type ignore
        
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound, loop=False)
            self.score += 1

        if arcade.check_for_collision_with_list(self.player_sprite, self.lava_list):
            arcade.play_sound(self.game_over_sound, loop= False)
            self.setup()
        
        if arcade.check_for_collision_with_list(self.player_sprite, self.exit_list):
            arcade.play_sound(self.next_level, loop=False)
            self.setup("maps/map2.txt")





            
    def on_draw(self) -> None:
        """Render the screen."""
        self.clear() # always start with self.clear()
        with self.camera.activate():
            self.wall_list.draw()
            self.coin_list.draw()
            self.player_sprite_list.draw()
            self.lava_list.draw()


        with self.camera_score.activate():
            w, h = arcade.get_window().get_size()
            SCORE_TEXT = f"SCORE {self.score}"
            arcade.draw_text(SCORE_TEXT, 10, h - 10, arcade.csscolor.WHITE, 18)





    def on_key_press(self, key: int, modifiers: int) -> None:
        """Called when the user presses a key on the keyboard."""
        match key:
            case arcade.key.RIGHT:
                # start moving to the right
                self.player_sprite.change_x = +PLAYER_MOVEMENT_SPEED
            case arcade.key.LEFT:
                # start moving to the left
                self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
            case arcade.key.UP:
                # jump by giving an initial vertical speed
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound, loop= False)
            case arcade.key.ESCAPE:
                # restart the game
                self.setup()



    def on_key_release(self, key: int, modifiers: int) -> None:
        """Called when the user releases a key on the keyboard."""
        match key:
            case arcade.key.RIGHT | arcade.key.LEFT:
                # stop lateral movement
                self.player_sprite.change_x = 0



        







