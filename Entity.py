import arcade
from abc import abstractmethod
import math
import random

class Entity(arcade.Sprite):
    def __init__(self, image_path: str, center_x: float, center_y: float, velocity_x: float, velocity_y: float, game_view: arcade.View) -> None:
        super().__init__(image_path, 0.5)
        self.center_x = center_x  # Set the initial x position
        self.center_y = center_y  # Set the initial y position
        self.change_x = velocity_x
        self.change_y = velocity_y  # Initial movement direction
        self.game = game_view

    @abstractmethod
    def movement(self) -> None:
        """Abstract method for the Movement of a monster"""
        pass

    def on_update(self, delta_time : float ) -> None:
        self.update(delta_time)
        self.movement()

class Blob(Entity):
    def __init__(self, center_x: float, center_y: float, game_view: arcade.View) -> None:
        velocity_x = 1
        velocity_y = 0
        super().__init__(":resources:images/enemies/slimeBlue.png", center_x, center_y, velocity_x, velocity_y, game_view)
        self.reverse_cooldown = 0  # Cooldown period after reversing direction

    def movement(self) -> None:
        """Handles blob movement and reverses direction when hitting walls."""
        # If the blob is in a cooldown period after reversing direction, skip movement
        if self.reverse_cooldown > 0:
            self.reverse_cooldown -= 1
            self.center_x += self.change_x
            return
        from gameview import GameView
        #assign the type hint for game to use the attribute wall_list
        self.game: GameView
        # Calculate the hitboxes for the blob
        right_hitbox = self.right + self.change_x
        left_hitbox = self.left + self.change_x
        ground_left = False
        ground_right = False

        # Check for walls in front of the blob
        walls_hit = arcade.check_for_collision_with_list(self, self.game.wall_list)
        if walls_hit:
            # Reverse direction if hitting a wall
            self.change_x = -self.change_x
            self.center_x += self.change_x  # Move back to avoid getting stuck
            self.reverse_cooldown = 10  # Set cooldown period to prevent immediate re-detection
        else:
            # Check if the blob is about to step off a platform (no ground below)
            ground_left = any(
                wall.collides_with_point((left_hitbox, self.bottom - 16))
                for wall in self.game.wall_list
            )
            ground_right = any(
                wall.collides_with_point((right_hitbox, self.bottom - 16))
                for wall in self.game.wall_list
            )

            if self.change_x > 0 and not ground_right:  # Moving right, no ground
                self.change_x = -1  # Turn left
            elif self.change_x < 0 and not ground_left:  # Moving left, no ground
                self.change_x = 1  # Turn right

        self.center_x += self.change_x  # Move the blob

class Bat(Entity):
    starting_x: float
    starting_y: float

    def __init__(self, center_x: float, center_y: float, game_view : arcade.View) -> None:
        velocity_x = 0
        velocity_y = 0
        self.starting_x = center_x
        self.starting_y = center_y
        super().__init__("assets/kenney-extended-enemies-png/bat.png", center_x, center_y, velocity_x, velocity_y, game_view)

    def movement(self) -> None:
        """Handles Bat movement with a normal distribution and takes into account the range of action."""
        if math.sqrt((self.starting_x - self.center_x) ** 2 + (self.starting_y - self.center_y) ** 2) <= 200:  # Range of action bounded by a circle of radius 200
            self.change_x += random.normalvariate(0, 0.05)
            self.change_y += random.normalvariate(0, 0.05)
            if abs(self.change_x) > 0.5:
                self.change_x *= 0.25
            if abs(self.change_y) > 0.5:
                self.change_y *= 0.25
        else:
            self.change_x = -(self.center_x - self.starting_x) * 0.007
            self.change_y = -(self.center_y - self.starting_y) * 0.007

    def on_update(self,delta_time : float)-> None:
        delta_time = 5 / 60
        return super().on_update(delta_time)
    
class Ghost(Entity):
    
    def __init__(self, center_x: float, center_y: float, game_view: arcade.View) -> None:
        velocity_x = 0
        velocity_y = 0
        super().__init__("assets/kenney-extended-enemies-png/ghost.png", center_x, center_y, velocity_x, velocity_y, game_view)
        self.starting_x = center_x
        self.starting_y = center_y

    def movement(self) -> None:
        """ Handles the ghost movement by moving towards the player. """
        from gameview import GameView
        self.game: GameView

        # Calculate the distance to the player
        player_x = self.game.player.center_x
        player_y = self.game.player.center_y
        distance = math.sqrt((self.center_x - player_x) ** 2 + (self.center_y - player_y) ** 2)
        # Move towards the player if within a certain range
        if distance < 300:
            self.change_x = (player_x - self.center_x) / distance * 2
            self.change_y = (player_y - self.center_y) / distance * 2
        else:
            self.change_x = 0
            self.change_y = 0















