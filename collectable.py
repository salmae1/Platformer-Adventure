from abc import abstractmethod
import arcade
from typing import TYPE_CHECKING
import time
if TYPE_CHECKING:
    from gameview import GameView

class Collectable(arcade.Sprite):
    """A class representing a collectable item in the game."""
    def __init__(self, image: str, center_x: float, center_y: float, scale: float = 1.0):
        """Initialize the collectable item."""
        super().__init__(image, scale=scale)
        self.center_x = center_x
        self.center_y = center_y
    @abstractmethod
    def effect_on_view(self,view: "GameView") -> None:
        """Apply the effect of the collectable on the player.
        This method should be overridden in subclasses to define specific effects.
        """
        pass
    def collect(self,view: "GameView")->None:
        """Collect  remove it from the sprite list."""
        self.effect_on_view(view)
        collect_sound = arcade.load_sound(":resources:sounds/coin1.wav", streaming=False)
        arcade.play_sound(collect_sound, loop=False)
        self.remove_from_sprite_lists()

class Coin(Collectable):
    """A class representing a coin collectable item."""
    def __init__(self, center_x: float, center_y: float)-> None:
        """Initialize the coin collectable item."""
        super().__init__(":resources:images/items/coinGold.png", center_x, center_y, scale= 0.5) 

    def effect_on_view(self, view: "GameView") -> None:
        """Apply the effect of collecting a coin on the player."""
        view.score += 1 


class Apple(Collectable):
    """A class representing an apple collectable item."""
    def __init__(self, center_x: float, center_y: float):
        """Initialize the apple collectable item."""
        super().__init__("assets/kenney-voxel-items-png/apple.png", center_x, center_y, scale= 0.5)

    def effect_on_view(self, view: "GameView") -> None:
        """Apply the effect of collecting an apple on the player."""
        view.player.hidden_time = time.time() + 3
        return   

    