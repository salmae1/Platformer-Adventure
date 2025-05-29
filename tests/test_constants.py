import pytest
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, PLAYER_MOVEMENT_SPEED,
    PLATFORM_MOVEMENT_SPEED_L, PLATFORM_MOVEMENT_SPEED_V,
    PLAYER_GRAVITY, PLAYER_JUMP_SPEED, ARROW_GRAVITY, ARROW_SPEED,
    tile_size, ASSETS, WEAPON, Platform, Arrow
)


def test_constants_values() -> None:
    assert WINDOW_WIDTH == 1280
    assert WINDOW_HEIGHT == 720
    assert PLAYER_MOVEMENT_SPEED == 5
    assert PLATFORM_MOVEMENT_SPEED_L == 1
    assert PLATFORM_MOVEMENT_SPEED_V == 0.5
    assert PLAYER_GRAVITY == 1
    assert PLAYER_JUMP_SPEED == 18
    assert ARROW_GRAVITY == 0.2
    assert ARROW_SPEED == 15
    assert tile_size == 64


def test_assets_dictionary() -> None:
    assert isinstance(ASSETS, dict)
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in ASSETS.items())

    required_keys = {"=", "-", "x", "*", "p", "£", "S", "E", "^", "|"}
    assert required_keys.issubset(ASSETS.keys())

    for k in required_keys:
        assert k in ASSETS
        assert ASSETS[k].endswith(".png") or ASSETS[k].startswith(":resources:")


def test_weapon_dictionary() -> None:
    assert isinstance(WEAPON, dict)
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in WEAPON.items())

    required_keys = {"sword", "bow", "arrow", "bowArrow"}
    assert required_keys.issubset(WEAPON.keys())

    assert WEAPON["sword"].endswith("sword_bronze.png")
    assert WEAPON["arrow"].endswith("arrow.png")


def test_arrow_enum() -> None:
    assert isinstance(Arrow.LEFT, Arrow)
    assert Arrow.LEFT.value == "←"
    assert Arrow.RIGHT.value == "→"
    assert Arrow.UP.value == "↑"
    assert Arrow.DOWN.value == "↓"

    directions = [e.value for e in Arrow]
    assert directions == ["←", "→", "↑", "↓"]


def test_platform_creation_and_access() -> None:
    block = [(0, 0), (1, 0)]
    bounds = {
        Arrow.LEFT: 0,
        Arrow.RIGHT: 2,
        Arrow.UP: 1,
        Arrow.DOWN: 0
    }

    platform = Platform(block, bounds)

    assert platform.block == block
    assert platform.bound_left == 0
    assert platform.bound_right == 2
    assert platform.bound_up == 1
    assert platform.bound_down == 0

    assert isinstance(platform.block, list)
    assert all(isinstance(coord, tuple) for coord in platform.block)
    assert all(isinstance(c, int) and len(coord) == 2 for coord in platform.block for c in coord)