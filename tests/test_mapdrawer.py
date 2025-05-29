import pytest
import arcade
from constants import Arrow, Platform
from mapdrawer import MapDrawer
from Entity import Blob, Bat, Ghost
import collectable
from gameview import GameView
from maploader import SWITCH


@pytest.fixture
def test_map_data() -> list[str]:
    """Carte de test """
    return [
        "........",
        "..^.|..E",
        "..o*vGp."
    ]

@pytest.fixture
def test_gameview(window: arcade.Window) -> GameView:
    view = GameView("maps/maptest.txt")  
    window.show_view(view)
    return view



def test_entities_to_SpriteList(test_map_data: list[str], test_gameview: GameView) -> None:
    drawer = MapDrawer(test_map_data, 8, 3, test_gameview)
    entity_list = drawer.entities_to_SpriteList(test_gameview)

    assert len(entity_list) == 3
    types = [type(e) for e in entity_list]
    assert Blob in types
    assert Bat in types
    assert Ghost in types


def test_switches_to_SpriteList(test_map_data: list[str], test_gameview: GameView) -> None:
    drawer = MapDrawer(test_map_data, 8, 3, test_gameview)

    switch_infos: dict[tuple[int, int], SWITCH] = {
        (2, 1): {
            "state": "off",
            "enabled": True,
            "switch_on": [],
            "switch_off": []
        }
    }

    switch_list, sprite_to_info = drawer.switches_to_SpriteList(switch_infos)

    assert len(switch_list) == 1
    switch_sprite = switch_list[0]
    assert isinstance(switch_sprite, arcade.Sprite)
    assert switch_sprite in sprite_to_info
    assert sprite_to_info[switch_sprite]["state"] == "off"
    assert isinstance(sprite_to_info[switch_sprite]["enabled"], bool)


def test_gates_to_SpriteList(test_map_data: list[str], test_gameview: GameView) -> None:
    drawer = MapDrawer(test_map_data, 8, 3, test_gameview)
    seen: set[tuple[int, int]] = set()
    gate_states = {(4, 1): False} 

    gate_list = drawer.gates_to_SpriteList(gate_states, seen)

    assert len(gate_list) == 1
    gate_sprite = gate_list[0]
    assert isinstance(gate_sprite, arcade.Sprite)
    assert (4, 1) in seen


def test_get_collectable_to_SpriteList(test_map_data: list[str], test_gameview: GameView) -> None:
    drawer = MapDrawer(test_map_data, 8, 3, test_gameview)
    items = drawer.get_collectable_to_SpriteList()

    assert len(items) == 2
    types = [type(i) for i in items]
    assert collectable.Coin in types
    assert collectable.Apple in types


def test_get_exit_to_SpriteList(test_map_data: list[str], test_gameview: GameView) -> None:
    drawer = MapDrawer(test_map_data, 8, 3, test_gameview)
    exits = drawer.get_exit_to_SpriteList()

    assert len(exits) == 1
    assert isinstance(exits[0], arcade.Sprite)


def test_Platform_to_SpriteList(test_gameview: GameView) -> None:
    test_platform = Platform(
        block=[(1, 1), (2, 1)],
        bounds={
            Arrow.LEFT: 0,
            Arrow.RIGHT: 3,
            Arrow.UP: 0,
            Arrow.DOWN: 2
        }
    )
    dummy_map = ["xxxxx"] * 3
    drawer = MapDrawer(dummy_map, 8, 3, test_gameview)

    wall_list :arcade.SpriteList[arcade.Sprite]= arcade.SpriteList()
    lava_list :arcade.SpriteList[arcade.Sprite]= arcade.SpriteList()
    seen : set[tuple[int, int]]= set()

    drawer.Platform_to_SpriteList(test_platform, wall_list, lava_list, seen)

    assert len(wall_list) == 2
    assert all(isinstance(s, arcade.Sprite) for s in wall_list)
    assert seen == {(1, 1), (2, 1)}