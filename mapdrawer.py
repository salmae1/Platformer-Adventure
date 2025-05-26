from arcade import Sprite,SpriteList,View
import utils
from typing import Final
from constants import ASSETS, tile_size , Arrow ,Platform , PLATFORM_MOVEMENT_SPEED_L, PLATFORM_MOVEMENT_SPEED_V
from Entity import Blob,Bat,Ghost,Entity
from enum import Enum
from maploader import SWITCH,GATE

class MapDrawer:
    __map_data: list[str]
    width: Final[int]
    height: Final[int]
    gameview: View

    def __init__(self, map_data: list[str], width: int, height: int,gameview: View) -> None:
        """Initialize the MapDrawer with map data and dimensions."""
        self.__map_data = map_data
        self.width = width
        self.height = height
        self.gameview = gameview
    
    @property
    def map_data(self) -> list[str]:
        """Get the map data."""
        return self.__map_data
    
    def Platform_to_SpriteList(self,platform:Platform,sprite_list : SpriteList[Sprite],seen:set[tuple[int,int]]) -> None:
        """Get the sprite list from a block."""
        
        #get the borders of the platform
        l,r,u,d= utils.get_borders(platform.block)
        # Iterate through the block and create sprites
        if platform:
            for x,y in platform.block:
                # Get the asset for the tile
                tile=self.map_data[y][x]
                if (x,y) not in seen:
                    print(platform.bound_left, platform.bound_right, platform.bound_up, platform.bound_down)
                    c_x,c_y = utils.coordinate(x), utils.coordinate(y)
                    # Create a sprite for the tile
                    sprite = Sprite(ASSETS[tile], center_x=c_x, center_y=c_y,scale=0.5)
                    sprite.change_x = PLATFORM_MOVEMENT_SPEED_L if platform.bound_left < l or platform.bound_right > r else 0
                    sprite.change_y = PLATFORM_MOVEMENT_SPEED_V if platform.bound_up > u or platform.bound_down < d else 0
                    # Set the boundaries of the sprite
                    sprite.boundary_right = c_x + max(utils.coordinate(platform.bound_right+0.5)-utils.coordinate(r), 0)
                    sprite.boundary_left = c_x + min(utils.coordinate(platform.bound_left-0.5)-utils.coordinate(l), 0)
                    sprite.boundary_top = c_y + max(utils.coordinate(platform.bound_up+0.5)-utils.coordinate(u), 0)
                    sprite.boundary_bottom = c_y + min(utils.coordinate(platform.bound_down-0.5)-utils.coordinate(d), 0)
                    sprite_list.append(sprite) if sprite not in sprite_list else None
                else:
                    continue
        #update the seen set
        seen.update(platform.block)
    
    import arcade
    def entities_to_SpriteList(self,gameview : arcade.View) -> SpriteList[Entity]:
        """Get the sprite list from entity asset."""
        sprite_list: SpriteList[Entity] = SpriteList()

        from gameview2 import GameView2
        self.gameview: GameView2 = gameview

        for y in range(self.height):
            for x in range(self.width):
                tile = self.map_data[y][x]
                if tile in {"o","v","G"}:
                    if tile == "o":
                        blob = Blob(utils.coordinate(x), utils.coordinate(y), self.gameview)
                        sprite_list.append(blob)
                    elif tile == "v":
                        bat = Bat(utils.coordinate(x), utils.coordinate(y),self.gameview)
                        sprite_list.append(bat)
                    elif tile == "G":
                        ghost = Ghost(utils.coordinate(x), utils.coordinate(y),self.gameview)
                        sprite_list.append(ghost)
                else:
                    continue
                

        return sprite_list
    
    def switches_to_SpriteList(self, switch_infos : dict[tuple[int,int],SWITCH]) -> tuple[SpriteList[Sprite],dict[Sprite, SWITCH]]:
        """Get the sprite list from switch asset."""
        switch_sprite_list: SpriteList[Sprite] = SpriteList()
        sprite_to_switch_info: dict[Sprite, SWITCH] = {}

        # Iterate through the map data to find switch tiles
        for y in range(self.height):
            for x in range(self.width):
                tile = self.map_data[y][x]

                if tile =="^":
                    switch_data = switch_infos.get((x, y), None)
                    if switch_data is None:
                        raise ValueError(f"missing configuraion for switch at {(x,y)}")
                    # Create a sprite for the switch
                    switch_state = switch_data["state"]
                    sprite = ASSETS[tile] 
                    switch = Sprite(sprite, center_x= utils.coordinate(x), center_y=utils.coordinate(y), scale=0.5)
                    switch_sprite_list.append(switch)
                    sprite_to_switch_info[switch] = switch_data
                else:
                    continue

        return switch_sprite_list, sprite_to_switch_info
    
    def gates_to_SpriteList(self, gate_states: dict[tuple[int,int],bool], seen: set[tuple[int,int]]) -> SpriteList[Sprite]:
        """Get the sprite list from gate asset."""
        gate_sprite_list: SpriteList[Sprite] = SpriteList()

        # Iterate through the map data to find gate tiles
        for y in range(self.height):
            for x in range(self.width):
                tile = self.map_data[y][x]
                c_x,c_y = utils.coordinate(x), utils.coordinate(y)
                if tile == "|" and (x, y) not in seen:
                    is_open = gate_states.get((x, y), False)

                    if not is_open:
                        gate = Sprite(ASSETS[tile], center_x= c_x, center_y=c_y, scale=0.5)
                        gate_sprite_list.append(gate)
                        seen.add((x, y))
                else:
                    continue
        # Return the sprite list of gates    
        return gate_sprite_list
    
    def get_coins_to_SpriteList(self) -> SpriteList[Sprite]:
        """Get the sprite list from coin asset."""
        coin_sprite_list: SpriteList[Sprite] = SpriteList(use_spatial_hash=True)
        # Iterate through the map data to find coin tiles
        for y in range(self.height):
            for x in range(self.width):
                tile = self.map_data[y][x]
                if tile == "*":
                    c_x, c_y = utils.coordinate(x), utils.coordinate(y)
                    coin = Sprite(ASSETS[tile], center_x=c_x, center_y=c_y, scale=0.5)
                    coin_sprite_list.append(coin)
                else:
                    continue
        return coin_sprite_list
    
    def get_exit_to_SpriteList(self) -> SpriteList[Sprite]:
        """Get the sprite list from exit asset."""
        exit_sprite_list: SpriteList[Sprite] = SpriteList(use_spatial_hash=True)
        # Iterate through the map data to find exit tiles
        for y in range(self.height):
            for x in range(self.width):
                tile = self.map_data[y][x]
                if tile == "E":
                    c_x, c_y = utils.coordinate(x), utils.coordinate(y)
                    exit_sprite = Sprite(ASSETS[tile], center_x=c_x, center_y=c_y, scale=0.5)
                    exit_sprite_list.append(exit_sprite)
                else:
                    continue
        return exit_sprite_list

    def get_lava_to_SpriteList(self) -> SpriteList[Sprite]:
        """Get the sprite list from lava asset."""
        lava_sprite_list: SpriteList[Sprite] = SpriteList(use_spatial_hash=True)
        # Iterate through the map data to find lava tiles
        for y in range(self.height):
            for x in range(self.width):
                tile = self.map_data[y][x]
                if tile == "£":
                    c_x, c_y = utils.coordinate(x), utils.coordinate(y)
                    lava = Sprite(ASSETS[tile], center_x=c_x, center_y=c_y, scale=0.5)
                    lava_sprite_list.append(lava)
                else:
                    continue
        return lava_sprite_list



