import arcade 
from Entity import Blob, Bat, Ghost
from unittest.mock import MagicMock
from gameview import GameView
import pytest
import random


@pytest.fixture
def mock_game_view(window: arcade.Window) -> GameView:
    view = GameView()
    window.show_view(view)
    return view


def test_blob_movement(mock_game_view: GameView) -> None:
    #Blob facing right

    ground = arcade.Sprite(center_x=70, center_y=104, width=100, height=20)
    mock_game_view.wall_list = arcade.SpriteList()
    mock_game_view.wall_list.append(ground)

    # Placer le blob juste au-dessus du sol
    blob = Blob(50, 100, mock_game_view)
    blob.change_x = 1
    blob.reverse_cooldown = 0
    blob.center_y = ground.top + blob.height / 2 + 1 

    previous_x = blob.center_x
    blob.movement()

    assert blob.center_x > previous_x


    #Case 2: Wall ahead, should reverse
    wall = arcade.Sprite(center_x=blob.center_x + 1, center_y=blob.center_y)
    mock_game_view.wall_list.append(wall)

    blob.center_x = wall.center_x - 1
    blob.change_x = 1
    blob.reverse_cooldown = 0

    blob.movement()
    assert blob.change_x == -1, "Blob should reverse direction after wall collision"
    assert blob.reverse_cooldown > 0

    #Case 3: Cooldown active, should just move
    blob.reverse_cooldown = 5
    blob.change_x = 1
    last_x = blob.center_x
    blob.movement()
    assert blob.center_x > last_x, "Blob should continue moving during cooldown"


def test_bat_movement(mock_game_view: GameView) -> None:
    bat = Bat(100, 100, mock_game_view)

    bat.center_x = 150
    bat.center_y = 150
    bat.change_x = 0.6
    bat.change_y = 0.6
    bat.movement()
    assert abs(bat.change_x) <= 0.5, "Bat change_x should be limited"
    assert abs(bat.change_y) <= 0.5, "Bat change_y should be limited"

    bat.center_x = 400
    bat.center_y = 400
    bat.movement()
    assert bat.change_x < 0, "Bat should move left toward original_x"
    assert bat.change_y < 0, "Bat should move down toward original_y"



def test_bat_on_update(mock_game_view: GameView) -> None:
    bat = Bat(100, 100, mock_game_view)
    old_x = bat.center_x
    old_y = bat.center_y

    bat.change_x = 1
    bat.change_y = 1

    bat.on_update(1 / 60)
    assert bat.center_x != old_x or bat.center_y != old_y



def test_ghost_movement(mock_game_view: GameView) -> None:
    ghost = Ghost(50, 50, mock_game_view)

    #Case1: Player within range
    mock_game_view.player.center_x = 60
    mock_game_view.player.center_y = 60
    ghost.movement()
    assert ghost.change_x != 0, "Ghost should move towards player X"
    assert ghost.change_y != 0, "Ghost should move towards player Y"

    #Case2: Player far away
    mock_game_view.player.center_x = 1000
    mock_game_view.player.center_y = 1000
    ghost.movement()
    assert ghost.change_x == 0, "Ghost should stop when player is out of range"
    assert ghost.change_y == 0