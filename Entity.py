import arcade 
from abc import abstractmethod
import math 
import random
class Entity(arcade.Sprite):
    def __init__(self, image_path, center_x : float , center_y: float ,velocity_x: float ,velocity_y : float , game_view) :
        super().__init__(image_path, 0.5)
        
        self.center_x = center_x  # Set the initial x position
        self.center_y = center_y  # Set the initial y position
        self.change_x = velocity_x  
        self.change_y = velocity_y   # Initial movement direction
        self.game = game_view

    @abstractmethod
    def movement(self)-> None :
        """Abstract method for the Movement of a monster"""
        pass
    
    def on_update(self, delta_time= 1/60)->None:
        self.update(delta_time)
        self.movement()

class Blob(Entity):

    def __init__(self, center_x: float, center_y: float ,game_view):
        velocity_x = 1
        velocity_y = 0
        super().__init__(":resources:images/enemies/slimeBlue.png", center_x , center_y, velocity_x, velocity_y , game_view)


    def movement(self) -> None:
        """Handles blob movement and reverses direction when hitting walls."""
        right_hitbox = self.right + self.change_x
        left_hitbox = self.left + self.change_x

        # Check for walls in front of the blob
        hit_walls = arcade.check_for_collision_with_list(self, self.game.wall_list)

        if hit_walls:  # If the blob is colliding with a wall, reverse direction
            self.change_x *= -1  
        else:
            # Check if the blob is about to step off a platform (no ground below)
            ground_left = any(
            wall.collides_with_point((left_hitbox, self.bottom - 1))
            for wall in self.game.wall_list
        )
            ground_right = any(
            wall.collides_with_point((right_hitbox, self.bottom - 1))
            for wall in self.game.wall_list
        )

        if self.change_x > 0 and not ground_right:  # Moving right, no ground
            self.change_x = -1  # Turn left
        elif self.change_x < 0 and not ground_left:  # Moving left, no ground
            self.change_x = 1  # Turn right

        self.center_x += self.change_x  # Move the blob


class Bat(Entity):
    starting_x : float
    starting_y : float
    def __init__(self, center_x: float, center_y: float ,game_view):
        velocity_x = 0
        velocity_y = 0
        self.starting_x = center_x
        self.starting_y = center_y
        super().__init__("assets/kenney-extended-enemies-png/bat.png", center_x , center_y, velocity_x,velocity_y,game_view)

    def movement(self)->None :
        """Handles Bat movement with a normal distribution and take into account the range of action."""
        if  math.sqrt((self.starting_x- self.center_x)**2 + (self.starting_y- self.center_y)**2) <= 200 : #range of action bounded by a circle of radius 500
            self.change_x += random.normalvariate(0, 0.05) 
            self.change_y += random.normalvariate(0, 0.05)
            if abs(self.change_x) > 0.5 :
                self.change_x*=0.25
            if abs(self.change_y) > 0.5 :
                self.change_y*= 0.25
        else :
            self.change_x = -(self.center_x-self.starting_x)*0.007
            self.change_y = -(self.center_y-self.starting_y)*0.007
            
            
           
    def on_update(self):
        delta_time = 5/60 
        return super().on_update(delta_time)
        
        











    

