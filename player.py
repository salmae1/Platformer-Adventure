import arcade
import math
from constants import WEAPON
from constants import PLAYER_MOVEMENT_SPEED, PLAYER_JUMP_SPEED, PLAYER_GRAVITY , ARROW_SPEED
import time
class Player(arcade.Sprite):
    """Player class representing the player character in the game."""
    sprite_list: arcade.SpriteList[arcade.Sprite]
    lives : int
    weapon: arcade.SpriteList[arcade.Sprite]
    right_pressed: bool 
    left_pressed: bool
    up_pressed: bool
    can_jump : bool
    hidden_time: float
    game_over :bool
    blink_state: bool
    sword_draw_time: float | None = None  # Time when the sword was drawn

    def __init__(self, image: str, center_x: float, center_y: float,scale: float = 0.5) -> None:
        """Initialize the player sprite."""
        super().__init__(image, center_x=center_x, center_y=center_y, scale=scale)
        self.change_x = 0
        self.change_y = 0

        self.can_jump = True
        self.right_pressed = False
        self.left_pressed = False
        self.up_pressed = False

        self.hidden_time = 0 #initialize invincibility time
        self.blink_state = False  # Initialize blink state
        self.game_over = False

        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav", streaming=False)

        self.sprite_list = arcade.SpriteList()
        self.sprite_list.append(self)

        self.sword = arcade.Sprite(
            WEAPON["sword"],
            scale=0.5 * 0.7,
        )

        self.bowArrow = arcade.Sprite(
            WEAPON["bowArrow"],
            scale=0.5 * 0.7,
        )

        self.weapon = arcade.SpriteList()
        self.weapon.append(self.sword)
        self.weapon.append(self.bowArrow)
        # Initialize the active weapon
        self.active_weapon_index = 1
        self.active_weapon_sprite = self.bowArrow
        self.sword_draw_time = None  # Initialize the sword draw time

    def update_player_speed(self)-> None :
        self.change_x = 0 
        if self.left_pressed and not self.right_pressed:
            self.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.change_x = + PLAYER_MOVEMENT_SPEED
        if self.up_pressed and self.can_jump:
                self.change_y = + PLAYER_JUMP_SPEED
                self.can_jump = False 
                play_jump_sound=arcade.play_sound(self.jump_sound, loop= False)

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


    def on_key_release(self, key : int , modifiers : int ) -> None :
        """Called when the user releases a key on the keyboard"""
        match key :
            case arcade.key.RIGHT :
                #stop lateral movement
                self.right_pressed =  False
                self.update_player_speed()
            case arcade.key.LEFT :
                self.left_pressed = False
                self.update_player_speed()
            case arcade.key.UP :
                self.up_pressed = False 
                self.update_player_speed()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int, camera: arcade.Camera2D) -> None:
        """Handle mouse press events."""
        # Unproject the mouse coordinates to world coordinates
        world_x, world_y, _ = camera.unproject((x, y))

        # Defensive check to avoid IndexError if weapon list is empty or index is invalid
        if len(self.weapon) < 2:
            # Ensure both sword and bowArrow are present
            if self.sword not in self.weapon:
                self.weapon.append(self.sword)
            if self.bowArrow not in self.weapon:
                self.weapon.append(self.bowArrow)
        if not self.weapon or not (0 <= self.active_weapon_index < len(self.weapon)):
            return  # Do nothing if weapon list is empty or index is out of range

        if button == arcade.MOUSE_BUTTON_RIGHT:
            # Switch weapon
            self.active_weapon_index = (self.active_weapon_index + 1) % len(self.weapon)
            self.active_weapon_sprite = self.weapon[self.active_weapon_index]

        active_weapon = self.weapon[self.active_weapon_index]

        if button == arcade.MOUSE_BUTTON_LEFT:
            if active_weapon == self.sword:
                # Calculate the angle of the sword towards the mouse position
                angle = 45 - math.degrees(math.atan2(world_y - self.center_y,
                                                     world_x - self.center_x))

                # Set the sword angle
                self.sword.angle = angle

                # Determine where to place the sword (either left or right of the player)
                if world_x >= self.center_x:
                    self.sword.center_x = self.right + 10
                else:
                    self.sword.center_x = self.left - 10

                # Adjust the vertical position slightly above or below the player
                self.sword.center_y = self.center_y

                # Add the sword to the sprite list to make it visible
                if self.sword not in self.sprite_list:
                    self.sprite_list.append(self.sword)

                self.sword_draw_time = time.time() # Record the time when the sword was drawn

            elif active_weapon == self.bowArrow:
                # Set the bowArrow's initial position and angle
                if x >= self.center_x:
                    self.bowArrow.center_x = self.right + 10
                else:
                    self.bowArrow.center_x = self.left - 10

                self.bowArrow.center_y = self.center_y

                # Calculate the angle of the bowArrow towards the mouse position
                bowArrow_angle = -math.degrees(math.atan2(y - self.center_y,
                                                          x - self.center_x))
                self.bowArrow.angle = bowArrow_angle

                # Add the bowArrow to the sprite list
                if self.bowArrow not in self.sprite_list:
                    self.sprite_list.append(self.bowArrow)

                # Store the target direction for the arrow
                self.arrow_target_x = world_x
                self.arrow_target_y = world_y

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
        """Handle mouse release events."""
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.sword in self.sprite_list:
                self.sprite_list.remove(self.sword)

            if self.bowArrow in self.sprite_list:
                self.bowArrow.remove_from_sprite_lists()

                # Create a new arrow for each release
                new_arrow = arcade.Sprite(
                    WEAPON["arrow"],
                    scale=0.5 * 0.7,
                )

                # Set the arrow's initial position
                new_arrow.center_x = self.center_x
                new_arrow.center_y = self.center_y

                # Calculate the arrow's velocity based on the bowArrow's angle
                arrow_angle = -math.degrees(math.atan2(self.arrow_target_y - self.center_y,
                                                       self.arrow_target_x - self.center_x))
                new_arrow.angle = arrow_angle
                new_arrow.change_x = ARROW_SPEED * math.cos(math.radians(arrow_angle))
                new_arrow.change_y = -ARROW_SPEED * math.sin(math.radians(arrow_angle))

                # Add the new arrow to the sprite list
                self.sprite_list.append(new_arrow)
