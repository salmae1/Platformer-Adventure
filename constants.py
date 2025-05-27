from enum import Enum
from typing import List, Dict, Final

WINDOW_WIDTH = 1280
"""Width of the window, in pixels."""
WINDOW_HEIGHT = 720
"""Height of the window, in pixels."""
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
"""Gravity applied to the arrow, in pixels per frame²."""
ARROW_SPEED = 15
"""Speed of the arrow, in pixels per frame."""
tile_size = 64
"""Size of a tile in pixels."""
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
class Arrow(Enum):
    LEFT = "←"
    RIGHT = "→"
    UP = "↑"
    DOWN = "↓"

class Platform:
    """Class representing a platform."""
    __block : List[tuple[int,int]]
    __bound_left: int
    __bound_right: int
    __bound_up: int
    __bound_down: int
    def __init__(self, block: list[tuple[int,int]], bounds: dict[Arrow,int]) -> None:
        """Initialize the Platform with a block and its bounds."""
        self.__block = block
        # Ensure not both horizontal and vertical bounds are set
        self.__bound_left = bounds[Arrow.LEFT]
        self.__bound_right = bounds[Arrow.RIGHT]
        self.__bound_up = bounds[Arrow.UP]
        self.__bound_down = bounds[Arrow.DOWN]
        #check if the platform is valid
    @property
    def block(self) -> list[tuple[int,int]]:
        """Get the block of the platform."""
        return self.__block
    @property
    def bound_left(self) -> int:
        """Get the left bound of the platform."""
        return self.__bound_left
    @property
    def bound_right(self) -> int:
        """Get the right bound of the platform."""
        return self.__bound_right
    @property
    def bound_up(self) -> int:
        """Get the upper bound of the platform."""
        return self.__bound_up
    @property
    def bound_down(self) -> int:
        """Get the lower bound of the platform."""
        return self.__bound_down
