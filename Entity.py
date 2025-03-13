import arcade 

class Blob(arcade.Sprite):

    def __init__(self, image_path, scale, center_x, center_y,game_view) :
        super().__init__(image_path, scale)  # Corrected super() call
        
        self.center_x = center_x  # Set the initial x position
        self.center_y = center_y  # Set the initial y position
        self.change_x = 1  # Initial movement direction
        self.game = game_view

    def movement_blob(self) -> None:
        """Handles blob movement and reverses direction when hitting walls."""
        from gameview import GameView
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

    def update_movement(self) -> None :
        self.update()
        self.movement_blob()


    

