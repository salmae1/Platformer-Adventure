from inspect import _empty
import utils
from  constants import tile_size , WINDOW_WIDTH, WINDOW_HEIGHT , ASSETS
import arcade
from arcade import Rect
from Entity import Entity
import maploader
import mapdrawer
import utils
from maploader import SWITCH, GATE
from constants import PLAYER_GRAVITY
from player import Player
from typing import Literal
import update
class GameView2(arcade.View):
    """Main in-game view."""
    player : Player
    wall_list: arcade.SpriteList[arcade.Sprite]
    platform_list: arcade.SpriteList[arcade.Sprite]
    entity_list: arcade.SpriteList[Entity]
    map_loader: maploader.MapLoader
    physics_engine:arcade.PhysicsEnginePlatformer
    camera: arcade.camera.Camera2D
    coin_list: arcade.SpriteList[arcade.Sprite]
    exit_list: arcade.SpriteList[arcade.Sprite]
    lava_list: arcade.SpriteList[arcade.Sprite]
    switch_list: arcade.SpriteList[arcade.Sprite]
    score : int
    next_map: str

    def __init__(self,filepath : str ="maps/map1.txt")-> None:
        # Magical incantion: initialize the Arcade view
        super().__init__()

        # Choose a nice comfy background color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        # Setup our game
        self.setup(filepath)
        self.camera = arcade.Camera2D()
        self.camera_score = arcade.camera.Camera2D()
        self.score = 0


    def setup(self,filepath :str = "maps/map1.txt")-> None:
        """Set up the game and initialize the variables."""
        # Load the map data
        self.map_loader = maploader.MapLoader(filepath)
        width, height, map_data, next_map, switches, gates = self.map_loader.read_map()
        # Set the next map
        self.next_map = next_map
        #set camera bounds 
        self.camera_bounds = arcade.LRBT(
        WINDOW_WIDTH / 2.0,
        width * tile_size ,
        WINDOW_HEIGHT / 2.0,
        height * tile_size ,
        )
        #switches_infos
        switch_infos:dict[tuple[int, int], SWITCH] = {}
        for switch_conf in switches:
            switch_pos = (switch_conf["x"], switch_conf["y"])
            switch_infos[switch_pos] = switch_conf

        #gates_infos
        self.gate_states = {}
        for gate_conf in gates:
            gate_pos = (gate_conf["x"], gate_conf["y"])
            is_open = (gate_conf.get("state", "closed") == "open")
            self.gate_states[gate_pos] = is_open
        
        #create a seen set to track visited tiles
        seen: set[tuple[int, int]] = set()

        #create the Spritelists
        map_drawer = mapdrawer.MapDrawer(map_data, width, height,self)
        #entities
        self.entity_list = map_drawer.entities_to_SpriteList(self)
        #switches
        self.switch_list, self.sprite_to_switch_info = map_drawer.switches_to_SpriteList(switch_infos)
        #gates
        self.gate_list = map_drawer.gates_to_SpriteList(self.gate_states, seen)

        #walls and platforms and the player
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.platform_list = arcade.SpriteList(use_spatial_hash=True)
        self.lava_list = arcade.SpriteList(use_spatial_hash=True)
        for y in range(height):
            for x in range(width):
                if (x, y) in seen:
                    continue
                elif map_data[y][x] == "S":
                    self.player = Player(ASSETS["S"], center_x=utils.coordinate(x), center_y=utils.coordinate(y), scale=0.5)
                else:
                    platform = utils.get_platform(x, y, map_data)
                    if platform.block:
                        print(platform.block)
                        # get the borders of the platform
                        left, right, up, down = utils.get_borders(platform.block)
                        # Check if the platform is moving
                        if platform.bound_left < left or platform.bound_right > right or \
                           platform.bound_up > up or platform.bound_down < down:
                            # If the platform is moving, add it to the platform list
                            map_drawer.Platform_to_SpriteList(platform, self.platform_list,seen)
                        else:
                            # If the platform is not moving, add it to the wall list
                            map_drawer.Platform_to_SpriteList(platform, self.wall_list,seen)
    #adding gates to the wall list
        for gate in self.gate_list:
            if gate not in self.wall_list:
                self.wall_list.append(gate)
    # Create the coin sprite list
        self.coin_list = map_drawer.get_coins_to_SpriteList()      
    # Create the exit sprite list
        self.exit_list = map_drawer.get_exit_to_SpriteList()    
    # Create the lava sprite list
        self.lava_list = map_drawer.get_lava_to_SpriteList()    
    # Create the physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            walls=self.wall_list,
            platforms=self.platform_list,  # Ensure moving platforms are included here
            gravity_constant=PLAYER_GRAVITY
        )
        
        self.physics_engine.disable_multi_jump()

    # Add a cooldown timer for sword-switch collision
        self._last_sword_switch_time = 0.0

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
                    if int(gate.center_x) == int(utils.coordinate(coord[0])) and int(gate.center_y) == int(utils.coordinate(coord[1])):
                        gate.remove_from_sprite_lists()
            if action["action"] == "close-gate":
                self.gate_states[coord] = False
                already_exists = any(
                    int(gate.center_x) == int(utils.coordinate(coord[0])) and int(gate.center_y) == int(utils.coordinate(coord[1]))
                    for gate in self.gate_list
                )
                if not already_exists:
                    gate_sprite = arcade.Sprite(ASSETS["|"], center_x=utils.coordinate(coord[0]), center_y=utils.coordinate(coord[1]), scale=0.5)
                    self.gate_list.append(gate_sprite)
                    self.wall_list.append(gate_sprite) if gate_sprite not in self.wall_list else None
            if action["action"] == "disable":
                switch_info["enabled"] = False

    def on_draw(self) -> None:
        """Render the screen."""
        self.clear() # always start with self.clear()
        self.camera.use()
        self.entity_list.draw()
        self.wall_list.draw()
        self.coin_list.draw()
        self.player.sprite_list.draw()
        self.lava_list.draw()
        self.exit_list.draw()
        self.platform_list.draw()
        self.switch_list.draw()
        self.gate_list.draw()
        with self.camera_score.activate():
            w, h = arcade.get_window().get_size()
            SCORE_TEXT = f"SCORE {self.score}"
            arcade.draw_text(SCORE_TEXT, w - 110, h - 30, 
                             arcade.csscolor.WHITE, 18)
            if self.player.active_weapon_index == 0:
                active_weapon_image = self.player.sword
            else:
                active_weapon_image = self.player.bowArrow
            weapon_rect = Rect( left=18, right=18+64, 
                               bottom=18, top=18+64, 
                               width=64, height=64,
                               x=40, y=h-30)
            arcade.draw_texture_rect(
                texture=active_weapon_image.texture,
                rect=weapon_rect
            )
    def on_key_press(self, key: int, modifiers: int) -> None:
        """Called when the user presses a key on the keyboard."""
        if key == arcade.key.SPACE:
            #reset the game
            gameover_sound = arcade.load_sound(":resources:sounds/gameover1.wav.", streaming = False)
            arcade.play_sound(gameover_sound,loop=False)
            self.score = 0
            self.setup("maps/map1.txt")
        self.player.on_key_press(key, modifiers)

    def on_key_release(self, key: int, modifiers: int) -> None:
        """Called when the user releases a key on the keyboard."""
        self.player.on_key_release(key, modifiers)
    
    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        """Called when the user presses a mouse button."""
        self.player.on_mouse_press(x, y, button, modifiers, self.camera)
    
    def on_mouse_release(self, x: float, y : float, button : int , modifiers : int) -> None:
        """Called when the user releases a mouse button."""
        self.player.on_mouse_release(x, y, button, modifiers)

    def pan_camera_to_player(self, panning_fraction: float = 0.3) -> None:
        """Pan the camera to follow the player."""
        self.camera.position = arcade.math.smerp_2d(
            self.camera.position,
            self.player.position,
            self.window.delta_time,
            panning_fraction
        )
        position = arcade.camera.grips.constrain_xy(
            self.camera.view_data,
            self.camera_bounds,
        )
        self.camera.position = arcade.Vec2(position[0], position[1])

    def check_for_gameover(self)-> None :

        touched_lava = any(lava.collides_with_point((self.player.center_x, self.player.bottom - 1)) for lava in self.lava_list)
        if touched_lava :
            gameover_sound = arcade.load_sound(":resources:sounds/gameover1.wav", streaming=False)
            arcade.play_sound(gameover_sound,loop=False)
            self.score = 0
            self.setup()

        if len(arcade.check_for_collision_with_list(self.player, self.entity_list)) != 0 :
            gameover_sound = arcade.load_sound(":resources:sounds/gameover1.wav", streaming=False)
            arcade.play_sound(gameover_sound,loop=False)
            self.score = 0
            self.setup()


    def on_update(self, delta_time: float) -> None:
        """Called once per frame, before drawing."""
        update.on_update(self, delta_time)


















