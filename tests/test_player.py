from constants import WEAPON, ASSETS
from constants import PLAYER_MOVEMENT_SPEED, PLAYER_JUMP_SPEED, PLAYER_GRAVITY , ARROW_SPEED
from player import Player 
import arcade
import math 


def test_update_player_speed() -> None:
    arcade.open_window(800, 600, "Test Update Player Speed")
    player = Player(ASSETS["S"], 0, 0)

    player.left_pressed = True
    player.right_pressed = False
    player.update_player_speed()
    assert player.change_x == -PLAYER_MOVEMENT_SPEED

    player.left_pressed = False
    player.right_pressed = True
    player.update_player_speed()
    assert player.change_x == PLAYER_MOVEMENT_SPEED

    player.up_pressed = True
    player.can_jump = True
    player.update_player_speed()
    assert player.change_y == PLAYER_JUMP_SPEED
    assert not player.can_jump

    arcade.close_window()


def test_on_key_press() -> None:
    arcade.open_window(800, 600, "Test Key Press")
    player = Player(ASSETS["S"], 0, 0)

    assert not player.right_pressed
    assert not player.left_pressed
    assert not player.up_pressed
    player.on_key_press(arcade.key.RIGHT, 0)
    assert player.right_pressed
    assert not player.left_pressed
    assert not player.up_pressed

    player.right_pressed = False
    player.on_key_press(arcade.key.LEFT, 0)
    assert player.left_pressed
    assert not player.right_pressed
    assert not player.up_pressed

    player.left_pressed = False
    player.on_key_press(arcade.key.UP, 0)
    assert player.up_pressed
    assert not player.right_pressed
    assert not player.left_pressed

    player.up_pressed = False
    player.on_key_press(arcade.key.SPACE, 0)
    assert not player.right_pressed
    assert not player.left_pressed
    assert not player.up_pressed

    player.right_pressed = False
    player.left_pressed = False
    player.up_pressed = False
    player.on_key_press(arcade.key.T, 0)
    assert not player.right_pressed
    assert not player.left_pressed
    assert not player.up_pressed


    arcade.close_window()

def test_on_key_release() -> None:
    arcade.open_window(800, 600, "Test Window")
    player = Player(ASSETS["S"], 100, 100)

    player.right_pressed = True
    player.left_pressed = True
    player.up_pressed = True

    player.on_key_release(arcade.key.RIGHT, 0)
    assert not player.right_pressed
    assert player.left_pressed
    assert player.up_pressed

    player.right_pressed = True
    player.on_key_release(arcade.key.LEFT, 0)
    assert not player.left_pressed
    assert player.right_pressed
    assert player.up_pressed

    player.left_pressed = True
    player.on_key_release(arcade.key.UP, 0)
    assert not player.up_pressed
    assert player.right_pressed
    assert player.left_pressed
    arcade.close_window()


def test_on_mouse_press() -> None:
    arcade.open_window(800, 600, "Test Mouse Press")
    player = Player(ASSETS["S"], 100, 100)
    camera = arcade.Camera2D()

    current_index = player.active_weapon_index
    player.on_mouse_press(200, 100, arcade.MOUSE_BUTTON_RIGHT, 0, camera)
    assert player.active_weapon_index == (current_index + 1) % 2
    assert player.active_weapon_sprite == player.weapon[player.active_weapon_index]

    player.active_weapon_index = player.weapon.index(player.sword)
    player.active_weapon_sprite = player.sword
    player.sprite_list = arcade.SpriteList()
    player.sprite_list.append(player)

    player.center_x = 100
    player.center_y = 100

    mouse_x = 200
    mouse_y = 100 

    player.on_mouse_press(mouse_x, mouse_y, arcade.MOUSE_BUTTON_LEFT, 0, camera)

    
    assert player.sword in player.sprite_list

    assert player.sword.center_y == player.center_y
 
    assert player.sword.center_x > player.center_x
   
    expected_angle = 45 - math.degrees(math.atan2(mouse_y - player.center_y, mouse_x - player.center_x))
    assert math.isclose(player.sword.angle, expected_angle, abs_tol=1.0)
   
    assert player.sword_draw_time is not None


    player.active_weapon_index = player.weapon.index(player.bowArrow)
    player.active_weapon_sprite = player.bowArrow
    player.sprite_list = arcade.SpriteList()
    player.sprite_list.append(player)

    player.on_mouse_press(50, 150, arcade.MOUSE_BUTTON_LEFT, 0, camera)

 
    assert player.bowArrow in player.sprite_list
  
    angle_expected = -math.degrees(math.atan2(150 - player.center_y, 50 - player.center_x))
    assert math.isclose(player.bowArrow.angle, angle_expected, abs_tol=1.0)


    assert player.bowArrow.center_x < player.center_x

    assert player.bowArrow.center_y == player.center_y

    assert player.arrow_target_x == 50
    assert player.arrow_target_y == 150

    arcade.close_window()

def test_on_mouse_release() -> None:
    arcade.open_window(800, 600, "Test Mouse Release")
    player = Player(ASSETS["S"], 100, 100)

    player.center_x = 100
    player.center_y = 100

 
    player.active_weapon_index = player.weapon.index(player.bowArrow)
    player.active_weapon_sprite = player.bowArrow
    player.sprite_list = arcade.SpriteList()
    player.sprite_list.append(player)
    player.sprite_list.append(player.bowArrow)

    player.arrow_target_x = 200
    player.arrow_target_y = 200


    n_before = len(player.sprite_list)
    player.on_mouse_release(200, 200, arcade.MOUSE_BUTTON_LEFT,0)
    n_after = len(player.sprite_list)

    assert n_after == n_before 
    arrow = player.sprite_list[-1]
    assert isinstance(arrow, arcade.Sprite)

 
    assert arrow.center_x == player.center_x
    assert arrow.center_y == player.center_y


    expected_angle = -math.degrees(math.atan2(
        player.arrow_target_y - player.center_y,
        player.arrow_target_x - player.center_x,
    ))
    expected_dx = math.cos(math.radians(expected_angle)) * 15
    expected_dy = -math.sin(math.radians(expected_angle)) * 15

    assert math.isclose(arrow.angle, expected_angle, abs_tol=1.0)
    assert math.isclose(arrow.change_x, expected_dx, rel_tol=1e-2)
    assert math.isclose(arrow.change_y, expected_dy, rel_tol=1e-2)


    player.sprite_list.append(player.sword)
    assert player.sword in player.sprite_list
    player.on_mouse_release(0, 0, arcade.MOUSE_BUTTON_LEFT,0)
    assert player.sword not in player.sprite_list

    arcade.close_window()

