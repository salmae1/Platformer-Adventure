import pytest
import arcade 
from typing import Dict, Tuple, Optional, Union
import time 
from types import SimpleNamespace

from constants import ARROW_GRAVITY
from gameview import GameView
from unittest.mock import MagicMock
from update import get_sprites_movement, switch_exit_movement, on_update


@pytest.fixture
def mock_game_view() -> GameView:
    view = MagicMock()
    view.platform_list = arcade.SpriteList()
    view.switch_list = arcade.SpriteList()
    view.exit_list = arcade.SpriteList()
    return view


def test_get_sprites_movement(mock_game_view : GameView) -> None:
 
    result = get_sprites_movement(mock_game_view)
    assert isinstance(result, dict)
    assert len(result) == 0


    platform = arcade.Sprite(center_x=100, center_y=100)
    switch = arcade.Sprite(center_x=100, center_y=132)
    mock_game_view.platform_list.append(platform)
    mock_game_view.switch_list.append(switch)

    result = get_sprites_movement(mock_game_view)
    assert len(result) == 1
    assert switch in result
    plat, dx, dy = result[switch]
    assert plat == platform
    assert dx == 0
    assert dy == 32

    exit_sprite = arcade.Sprite(center_x=100, center_y=132)
    mock_game_view.exit_list.append(exit_sprite)

    result = get_sprites_movement(mock_game_view)
    assert len(result) == 2
    assert exit_sprite in result
    plat, dx, dy = result[exit_sprite]
    assert plat == platform
    assert dx == 0
    assert dy == 32


    new_platform = arcade.Sprite(center_x=200, center_y=68)
    new_switch = arcade.Sprite(center_x=200, center_y=100)
    mock_game_view.platform_list.append(new_platform)
    mock_game_view.switch_list.append(new_switch)

    result = get_sprites_movement(mock_game_view)
    assert new_switch in result
    plat, dx, dy = result[new_switch]
    assert plat == new_platform
    assert dx == 0
    assert dy == 32


def test_switch_exit_movement() ->None:

    switch = arcade.Sprite(center_x=0, center_y=0)
    platform = arcade.Sprite(center_x=100, center_y=100)
    mapping: Dict[arcade.Sprite, Tuple[arcade.Sprite, float, float]] = {
        switch: (platform, -20, 30)
    }

    switch_exit_movement(mapping)
    assert switch.center_x == 80
    assert switch.center_y == 130


    free_switch = arcade.Sprite(center_x=10, center_y=10)

    mapping2: Dict[arcade.Sprite, Tuple[arcade.Sprite | None, float, float]] = {
        free_switch: (None, 0, 0)
    }

    try:
        switch_exit_movement(mapping)
        assert free_switch.center_x == 10
        assert free_switch.center_y == 10
    except Exception as e:
        pytest.fail(f"Ne doit pas planter si plateforme est None : {e}")



def test_on_update() -> None:
    mock_game_view = MagicMock()
    mock_game_view.physics_engine = MagicMock()
    mock_game_view.physics_engine.update = MagicMock()
    mock_game_view.physics_engine.can_jump.return_value = True
    mock_game_view.pan_camera_to_player = MagicMock()
    mock_game_view.check_for_gameover = MagicMock()
    mock_game_view.run_switch = MagicMock()
    mock_game_view.setup = MagicMock()
    mock_game_view.next_map = "map2.txt"
    mock_game_view._last_sword_switch_time = 0

    class TestPlayer(arcade.Sprite):
        def __init__(self) ->None:
            super().__init__(center_x=0, center_y=0)
            self.change_x = 2
            self.change_y = 3
            self.sprite_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
            self.weapon: Union[list[arcade.Sprite], arcade.SpriteList[arcade.Sprite]] = arcade.SpriteList()
            self.active_weapon_index = 0
            self.sword_draw_time: Optional[float] = None 
            self.hidden_time = time.time() + 1
            self.blink_state = False
            self.alpha = 255
            self.can_jump = False

    player = TestPlayer()
    mock_game_view.player = player

    mock_game_view.collectable_list = arcade.SpriteList()
    mock_game_view.entity_list = arcade.SpriteList()
    mock_game_view.exit_list = arcade.SpriteList()
    mock_game_view.wall_list = arcade.SpriteList()
    mock_game_view.lava_list = arcade.SpriteList()
    mock_game_view.platform_list = arcade.SpriteList()
    mock_game_view.switch_list = arcade.SpriteList()
    mock_game_view.sprites_to_move = {}

    on_update(mock_game_view, 1/60)


    assert mock_game_view.player.can_jump is True
    mock_game_view.pan_camera_to_player.assert_called()
    mock_game_view.physics_engine.update.assert_called()
    mock_game_view.check_for_gameover.assert_called()

 
    class TestCollectable(arcade.Sprite):
        def collect(self, gameview: GameView) ->None:
            self.collected = True

    collectable = TestCollectable(center_x=0, center_y=0)
    mock_game_view.collectable_list.append(collectable)
    on_update(mock_game_view, 1/60)
    assert hasattr(collectable, "collected")

    class TestEntity(arcade.Sprite):
        def __init__(self) ->None:
            super().__init__(center_x=0, center_y=0)
            self.updated = False

        def on_update(self, delta_time:float) ->None:
            self.updated = True

    entity = TestEntity()
    mock_game_view.entity_list.append(entity)
    on_update(mock_game_view, 1/60)
    assert entity.updated


    arrow = arcade.Sprite(center_x=0, center_y=10)
    mock_game_view.player.sprite_list.append(arrow)
    on_update(mock_game_view, 1/60)
    assert arrow.change_y < 0


    weapon = arcade.Sprite()
    mock_game_view.player.weapon.append(weapon)
    mock_game_view.player.sprite_list.append(weapon)
    on_update(mock_game_view, 1/60)
    assert weapon.change_x == 2
    assert weapon.change_y == 3


    class TestMonster(arcade.Sprite):
        def __init__(self)->None:
            super().__init__(center_x=0, center_y=0)
            self.removed = False

        def remove_from_sprite_lists(self)->None:
            self.removed = True

        def on_update(self, delta_time: float) -> None:
            pass

    monster = TestMonster()
    mock_game_view.entity_list.append(monster)

    class TestSwitch(arcade.Sprite):
        def __init__(self)->None:
            super().__init__(center_x=0, center_y=0)

    switch = TestSwitch()
    mock_game_view.switch_list.append(switch)

    sword = arcade.Sprite(center_x=0, center_y=0)
    mock_game_view.player.weapon = arcade.SpriteList()
    mock_game_view.player.weapon.append(sword)
    mock_game_view.player.sprite_list.append(sword)

    mock_game_view.player.sword_draw_time = time.time()

    on_update(mock_game_view, 1/60)

    assert monster.removed, "Monster should have been removed from sprite lists"
    mock_game_view.run_switch.assert_called()

    player.blink_state = False
    on_update(mock_game_view, 1/60)
    assert player.alpha in (100, 220)


