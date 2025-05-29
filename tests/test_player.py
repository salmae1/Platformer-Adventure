import pytest
import arcade
import math
from constants import ASSETS, WEAPON, PLAYER_MOVEMENT_SPEED, PLAYER_JUMP_SPEED, ARROW_SPEED
from player import Player


@pytest.fixture
def test_player(window: arcade.Window) -> Player:
    player = Player(ASSETS["S"], 100, 100)
    arcade.set_window(window)
    return player

@pytest.fixture
def test_camera() -> arcade.Camera2D:
    return arcade.Camera2D()


def test_update_player_speed(test_player: Player) -> None:

    test_player.left_pressed = True
    test_player.right_pressed = False
    test_player.update_player_speed()
    assert test_player.change_x == -PLAYER_MOVEMENT_SPEED

    test_player.left_pressed = False
    test_player.right_pressed = True
    test_player.update_player_speed()
    assert test_player.change_x == PLAYER_MOVEMENT_SPEED

    test_player.up_pressed = True
    test_player.can_jump = True
    test_player.update_player_speed()
    assert test_player.change_y == PLAYER_JUMP_SPEED
    assert not test_player.can_jump


def test_on_key_press(test_player: Player) -> None:

    assert not test_player.right_pressed
    assert not test_player.left_pressed
    assert not test_player.up_pressed

    test_player.on_key_press(arcade.key.RIGHT, 0)
    assert test_player.right_pressed

    test_player.right_pressed = False
    test_player.on_key_press(arcade.key.LEFT, 0)
    assert test_player.left_pressed

    test_player.left_pressed = False
    test_player.on_key_press(arcade.key.UP, 0)
    assert test_player.up_pressed

    test_player.on_key_press(arcade.key.SPACE, 0)
    test_player.on_key_press(arcade.key.T, 0)



def test_on_key_release(test_player: Player) -> None:

    test_player.right_pressed = True
    test_player.left_pressed = True
    test_player.up_pressed = True

    test_player.on_key_release(arcade.key.RIGHT, 0)
    assert not test_player.right_pressed

    test_player.on_key_release(arcade.key.LEFT, 0)
    assert not test_player.left_pressed

    test_player.on_key_release(arcade.key.UP, 0)
    assert not test_player.up_pressed


def test_on_mouse_press(test_player: Player, test_camera: arcade.Camera2D) -> None:
    current_index = test_player.active_weapon_index
    test_player.on_mouse_press(200, 100, arcade.MOUSE_BUTTON_RIGHT, 0, test_camera)
    assert test_player.active_weapon_index == (current_index + 1) % 2
    assert test_player.active_weapon_sprite == test_player.weapon[test_player.active_weapon_index]


    test_player.active_weapon_index = test_player.weapon.index(test_player.sword)
    test_player.active_weapon_sprite = test_player.sword
    test_player.sprite_list = arcade.SpriteList()
    test_player.sprite_list.append(test_player)

    test_player.center_x = 100
    test_player.center_y = 100

    mouse_x = 200
    mouse_y = 100
    test_player.on_mouse_press(mouse_x, mouse_y, arcade.MOUSE_BUTTON_LEFT, 0, test_camera)

    assert test_player.sword in test_player.sprite_list
    assert test_player.sword.center_y == test_player.center_y
    assert test_player.sword.center_x > test_player.center_x

    expected_angle = 45 - math.degrees(math.atan2(mouse_y - test_player.center_y, mouse_x - test_player.center_x))
    assert math.isclose(test_player.sword.angle, expected_angle, abs_tol=1.0)
    assert test_player.sword_draw_time is not None


    test_player.active_weapon_index = test_player.weapon.index(test_player.bowArrow)
    test_player.active_weapon_sprite = test_player.bowArrow
    test_player.sprite_list = arcade.SpriteList()
    test_player.sprite_list.append(test_player)

    test_player.on_mouse_press(50, 150, arcade.MOUSE_BUTTON_LEFT, 0, test_camera)

    assert test_player.bowArrow in test_player.sprite_list
    angle_expected = -math.degrees(math.atan2(150 - test_player.center_y, 50 - test_player.center_x))
    assert math.isclose(test_player.bowArrow.angle, angle_expected, abs_tol=1.0)
    assert test_player.bowArrow.center_x < test_player.center_x
    assert test_player.bowArrow.center_y == test_player.center_y
    assert test_player.arrow_target_x == 50
    assert test_player.arrow_target_y == 150


def test_on_mouse_release(test_player: Player) -> None:
    test_player.active_weapon_index = test_player.weapon.index(test_player.bowArrow)
    test_player.active_weapon_sprite = test_player.bowArrow
    test_player.sprite_list = arcade.SpriteList()
    test_player.sprite_list.append(test_player)
    test_player.sprite_list.append(test_player.bowArrow)

    test_player.center_x = 100
    test_player.center_y = 100
    test_player.arrow_target_x = 200
    test_player.arrow_target_y = 200

    n_before = len(test_player.sprite_list)
    test_player.on_mouse_release(200, 200, arcade.MOUSE_BUTTON_LEFT, 0)
    n_after = len(test_player.sprite_list)

    assert n_after == n_before
    arrow = test_player.sprite_list[-1]
    assert isinstance(arrow, arcade.Sprite)
    assert arrow.center_x == test_player.center_x
    assert arrow.center_y == test_player.center_y

    expected_angle = -math.degrees(math.atan2(
        test_player.arrow_target_y - test_player.center_y,
        test_player.arrow_target_x - test_player.center_x,
    ))
    expected_dx = math.cos(math.radians(expected_angle)) * ARROW_SPEED
    expected_dy = -math.sin(math.radians(expected_angle)) * ARROW_SPEED

    assert math.isclose(arrow.angle, expected_angle, abs_tol=1.0)
    assert math.isclose(arrow.change_x, expected_dx, rel_tol=1e-2)
    assert math.isclose(arrow.change_y, expected_dy, rel_tol=1e-2)

 
    test_player.sprite_list.append(test_player.sword)
    assert test_player.sword in test_player.sprite_list
    test_player.on_mouse_release(0, 0, arcade.MOUSE_BUTTON_LEFT, 0)
    assert test_player.sword not in test_player.sprite_list
