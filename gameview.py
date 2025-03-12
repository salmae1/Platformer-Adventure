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
    "S": ":resources:/images/animated_characters/female_person/femalePerson_idle.png"
}




class GameView(arcade.View):
    """Main in-game view."""


    player_sprite: arcade.Sprite
    player_sprite_list: arcade.SpriteList[arcade.Sprite]
    wall_list: arcade.SpriteList[arcade.Sprite]

    physics_engine: arcade.PhysicsEnginePlatformer

    camera : arcade.camera.Camera2D



    def __init__(self) -> None:
        # Magical incantion: initialize the Arcade view
        super().__init__()

        # Choose a nice comfy background color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        self.wall_list = arcade.SpriteList(use_spatial_hash = True)
        self.coin_list = arcade.SpriteList(use_spatial_hash = True)

        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav", streaming=False)
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav", streaming= False)


        # Setup our game
        self.setup()



    def read_map(self, file_path):
        """read and analyse the map."""
    
        with open(file_path, 'r', encoding="utf-8", newline='') as f:
            lines = f.readlines()
        

        width = height = 0
        index = 0

        # Configuration
        while index < len(lines) and lines[index].strip()!= "---":
            key, value = lines[index].strip().split(": ")
            if key == "width":
                width = int(value)
            elif key == "height":
                height = int(value)
            index += 1
        

        index += 1
        map_data = []

        # Characters
        while index < len(lines) and lines[index].strip() != "---":
            map_data.append(lines[index].rstrip("\n"))
            index += 1
        

        return width, height, map_data
    

        


    def setup(self) -> None:
        """Set up the game here."""

        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            center_x=64,
            center_y=128
            )
        self.player_sprite_list = arcade.SpriteList()
        self.player_sprite_list.append(self.player_sprite)

        width, height, map_data = self.read_map("maps/map1.txt")


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

        
        

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.wall_list,
            gravity_constant=PLAYER_GRAVITY
        )

        self.camera = arcade.camera.Camera2D()

        


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


    def on_draw(self) -> None:
        """Render the screen."""
        self.clear() # always start with self.clear()
        with self.camera.activate():
            self.wall_list.draw()
            self.coin_list.draw()
            self.player_sprite_list.draw()



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



        







