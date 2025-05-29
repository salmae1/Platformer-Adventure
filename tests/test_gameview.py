import arcade
import math
import time
import pytest
from unittest.mock import MagicMock
from typing import Generator
import utils
from gameview import GameView
from player import Player
from Entity import Blob
from constants import PLAYER_JUMP_SPEED, PLAYER_MOVEMENT_SPEED


@pytest.fixture(scope="session", autouse=True)
def arcade_window()-> Generator[None, None, None]:
    arcade.open_window(800, 600, "Test")
    yield
    arcade.close_window()

@pytest.fixture
def view() -> GameView:
    return GameView("maps/maptest.txt")

def test_setup(view:GameView) -> None:

    assert isinstance(view.player, Player)
    assert view.player.lives == view.current_lives
    assert view.score == 0
    assert view.current_lives == 3
    assert isinstance(view.next_map, str)

    assert isinstance(view.wall_list, arcade.SpriteList)
    assert isinstance(view.platform_list, arcade.SpriteList)
    assert isinstance(view.lava_list, arcade.SpriteList)
    assert isinstance(view.moving_lava, arcade.SpriteList)
    assert isinstance(view.switch_list, arcade.SpriteList)
    assert isinstance(view.gate_list, arcade.SpriteList)
    assert isinstance(view.entity_list, arcade.SpriteList)
    assert isinstance(view.collectable_list, arcade.SpriteList)
    assert isinstance(view.exit_list, arcade.SpriteList)
    assert isinstance(view.heart_list, arcade.SpriteList)
    assert isinstance(view.physics_engine, arcade.PhysicsEnginePlatformer)

    assert len(view.wall_list) > 0 or len(view.platform_list) > 0
    assert len(view.heart_list) == 3
    assert all(h.texture for h in view.heart_list)

    assert isinstance(view.sprite_to_switch_info, dict)
    assert all(isinstance(s, arcade.Sprite) for s in view.switch_list)
    assert all(s in view.sprite_to_switch_info for s in view.switch_list)

    assert view.camera_bounds.right > view.camera_bounds.left
    assert view.camera_bounds.top > view.camera_bounds.bottom

    assert isinstance(view._last_sword_switch_time, float)
    assert isinstance(view.sprites_to_move, dict)
    assert all(isinstance(k, arcade.Sprite) for k in view.sprites_to_move.keys())
    
    assert all(isinstance(v, dict) for v in view.sprite_to_switch_info.values())
    assert all("state" in v and "enabled" in v for v in view.sprite_to_switch_info.values())
    assert all(v["state"] in {"on", "off"} for v in view.sprite_to_switch_info.values())
    assert all(isinstance(v["enabled"], bool) for v in view.sprite_to_switch_info.values())
    assert all(isinstance(v.get("switch_on", []), list) and isinstance(v.get("switch_off", []), list)
               for v in view.sprite_to_switch_info.values())

    for switch, info in view.sprite_to_switch_info.items():
        assert isinstance(switch, arcade.Sprite)
        assert switch.texture is not None

    assert all(
        isinstance(k, tuple) and isinstance(v, bool) for k, v in view.gate_states.items()
    )

    for (x, y), state in view.gate_states.items():
        if not state:
            found = any(
                int(g.center_x) == utils.coordinate(x) and int(g.center_y) == utils.coordinate(y)
                for g in view.gate_list
            )
            if not found:
                print(f" Gate fermé introuvable en position logique ({x}, {y}) = ({utils.coordinate(x)}, {utils.coordinate(y)})")
            assert found


def test_on_draw(view:GameView) -> None:

    assert isinstance(view.player, Player)
    assert view.camera is not None
    assert view.camera_score is not None

    assert view.score >= 0
    assert view.player.active_weapon_index in (0, 1)
    assert hasattr(view.player, "sword")
    assert hasattr(view.player, "bowArrow")
    assert hasattr(view.player.sword, "texture")
    assert hasattr(view.player.bowArrow, "texture")

    try:
        view.on_draw()
    except Exception as e:
        assert False, f"on_draw() raised an exception: {e}"

    active = view.player.active_weapon_sprite
    assert active in (view.player.sword, view.player.bowArrow)


def test_run_switch(view:GameView) -> None:
    
    if not view.switch_list:
        pytest.skip("Pas de switch sur cette carte")


    switch = arcade.Sprite()
    switch.center_x = 0
    switch.center_y = 0

    gate = arcade.Sprite()
    gate.center_x = utils.coordinate(1)
    gate.center_y = utils.coordinate(1)
    view.gate_list.append(gate)

    view.sprite_to_switch_info[switch] = {
        "enabled": True,
        "state": "off",
        "switch_on": [
            {"x": 1, "y": 1, "action": "open-gate"},
            {"x": 1, "y": 1, "action": "disable"}
        ],
        "switch_off": [
            {"x": 1, "y": 1, "action": "close-gate"}
        ]
    }

    view.run_switch(switch)

    info = view.sprite_to_switch_info[switch]
    assert info["state"] == "on"
    assert not info["enabled"]
    assert view.gate_states[(1, 1)] is True
    assert all(
        int(g.center_x) != 64 or int(g.center_y) != 64 for g in view.gate_list
    )

    info["enabled"] = True
    before_count = len(view.gate_list)
    view.run_switch(switch)
    after_count = len(view.gate_list)

    assert str(info["state"]) == "off"
    assert view.gate_states[(1, 1)] is False
    assert after_count > before_count




def test_check_for_gameover(view:GameView) -> None:


    lava = arcade.Sprite(center_x=view.player.center_x, center_y=view.player.bottom - 1)
    lava.texture = arcade.make_soft_square_texture(32, arcade.color.RED, 255)
    view.lava_list.append(lava)

    view.player.lives = 2
    view.score = 50
    view.current_lives = 1
    view.player.hidden_time = 0

    view.check_for_gameover()

    assert view.score == 0
    assert view.current_lives == 3
    assert view.player.lives == 3 

    view.player.lives = 1
    view.score = 100
    view.current_lives = 1
    view.entity_list.clear()

    enemy = Blob(view.player.center_x, view.player.center_y, view)
    enemy.texture = arcade.make_soft_square_texture(32, arcade.color.BLUE, 255)
    view.entity_list.append(enemy)
    view.player.hidden_time = 0

    view.check_for_gameover()
    
    assert view.score == 0
    assert view.current_lives == 3
    assert view.player.lives == 3


    view.entity_list.clear()
    view.player.lives = 2
    view.current_lives = 2
    view.player.hidden_time = 0

    view.check_for_gameover()
    assert view.score == 0
    assert view.current_lives == 2
    assert view.player.lives == 2




def test_pan_camera_to_player(view:GameView) -> None:

    original_position = view.camera.position
    view.player.center_x += 100
    view.player.center_y += 50
    view.player.position = arcade.Vec2(view.player.center_x, view.player.center_y)

    view.pan_camera_to_player(panning_fraction=1.0)

    new_position = view.camera.position
    assert new_position != original_position
    assert isinstance(new_position, arcade.Vec2)
    assert new_position.x >= 0 and new_position.y >= 0

    assert view.camera_bounds.left < view.camera_bounds.right
    assert view.camera_bounds.bottom < view.camera_bounds.top


def test_on_key_press(view:GameView) -> None:
    
    view.score = 99
    view.on_key_press(arcade.key.SPACE, 0)
    assert view.score == 0
    assert isinstance(view.player, Player)

    view.on_key_press(arcade.key.RIGHT, 0)
    assert view.player.right_pressed
    assert view.player.change_x == PLAYER_MOVEMENT_SPEED

    view.on_key_release(arcade.key.RIGHT, 0)

    view.on_key_press(arcade.key.LEFT, 0)
    assert view.player.left_pressed
    assert view.player.change_x == -PLAYER_MOVEMENT_SPEED

    view.player.can_jump = True
    view.on_key_press(arcade.key.UP, 0)
    assert view.player.up_pressed
    assert view.player.change_y == PLAYER_JUMP_SPEED



def test_on_key_release(view:GameView) -> None:
   
    view.player.right_pressed = True
    view.player.left_pressed = True
    view.player.up_pressed = True

    view.on_key_release(arcade.key.RIGHT, 0)
    assert not view.player.right_pressed

    view.on_key_release(arcade.key.LEFT, 0)
    assert not view.player.left_pressed

    view.on_key_release(arcade.key.UP, 0)
    assert not view.player.up_pressed



def test_on_mouse_press(view:GameView) -> None:


    old_index = view.player.active_weapon_index
    view.on_mouse_press(200, 200, arcade.MOUSE_BUTTON_RIGHT, 0)
    assert view.player.active_weapon_index != old_index

    view.player.active_weapon_index = 0 
    view.player.active_weapon_sprite = view.player.sword
    view.on_mouse_press(300, 300, arcade.MOUSE_BUTTON_LEFT, 0)
    assert view.player.sword in view.player.sprite_list



def test_on_mouse_release(view:GameView) -> None:
    
    view.player.active_weapon_index = 1
    view.player.active_weapon_sprite = view.player.bowArrow
    view.player.arrow_target_x = 300
    view.player.arrow_target_y = 300
    view.player.sprite_list.append(view.player.bowArrow)

    nb_before = len(view.player.sprite_list)
    view.on_mouse_release(300, 300, arcade.MOUSE_BUTTON_LEFT, 0)
    nb_after = len(view.player.sprite_list)

    assert nb_after == nb_before
    arrow = view.player.sprite_list[-1]
    assert arrow.center_x == view.player.center_x
    assert arrow.center_y == view.player.center_y




def test_on_update(view: GameView) -> None:
    view.player.change_x = 5
    view.player.change_y = 10
    old_x = view.player.center_x
    old_y = view.player.center_y

    try:
        view.on_update(1 / 60)
    except Exception as e:
        assert False, f"on_update() a planté : {e}"

    assert view.player.center_x != old_x
    assert view.player.center_y != old_y