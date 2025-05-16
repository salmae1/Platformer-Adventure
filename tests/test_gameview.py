import arcade 
import pytest
import math
from gameview import GameView
from Entity import Entity, Blob, Bat





def test_read_map() -> None:
    arcade.open_window(800, 600, "Test Window")
    view = GameView()
    width, height, map_data, next_map = view.read_map("maps/map3.txt")
    assert width == 5
    assert height == 3
    assert next_map == "map4.txt"
    assert map_data == [
    '*  * ',
    '=====                    *        *',
    '                     o   x  o     x',
    '              ==========', '',
    '    ======',
    '        ',
    '        ===',
    '        ',
    '        ================',
    '        ',
    '                   o *',
    '                ========= =====',
    '==========£££££££££££££££££££££££££££££££££======='
    ]
    arcade.close_window()

def test_setup() -> None:
    arcade.open_window(800, 600, "Test Window")
    view = GameView()
    view.setup("maps/map3.txt")

    assert view.score == 0

    assert view.player_sprite in view.player_sprite_list
    assert isinstance(view.player_sprite, arcade.Sprite)

    assert str(view.weapon[0].texture.file_path).endswith("sword_bronze.png")
    assert str(view.weapon[1].texture.file_path).endswith("bow.png")
    assert view.active_weapon_sprite == view.bow

    assert len(view.coin_list) == 5     
    assert len(view.Entities) == 3         
    assert len(view.wall_list) >= 50 
    assert len(view.lava_list) == 33        
    assert len(view.exit_list) == 0        
    
    width, height, map_data, next_map = view.read_map("maps/map3.txt")
    assert width == 5
    assert height == 3
    assert next_map == "map4.txt"

    arcade.close_window()




def test_check_for_gameover() -> None:
    arcade.open_window(800, 600, "Test Window")
    view = GameView()
    view.setup("maps/map3.txt")

    old_score = view.score
    old_entities = list(view.Entities)
    old_walls = list(view.wall_list)

    lava = arcade.Sprite(center_x=view.player_sprite.center_x, center_y=view.player_sprite.center_y)
    view.lava_list.append(lava)

    view.check_for_gameover()

    assert view.score == 0
    assert list(view.Entities) != old_entities  
    assert view.wall_list != old_walls  

    arcade.close_window()


def test_on_key_press() -> None:
    arcade.open_window(800, 600, "Test Window")
    view = GameView()
    view.setup("maps/map3.txt")

    assert not view.right_pressed
    assert not view.left_pressed
    assert not view.up_pressed
    view.on_key_press(arcade.key.RIGHT, 0)
    assert view.right_pressed
    assert not view.left_pressed
    assert not view.up_pressed

    view.right_pressed = False
    view.on_key_press(arcade.key.LEFT, 0)
    assert view.left_pressed
    assert not view.right_pressed
    assert not view.up_pressed

    view.left_pressed = False
    view.on_key_press(arcade.key.UP, 0)
    assert view.up_pressed
    assert not view.right_pressed
    assert not view.left_pressed

    view.up_pressed = False
    view.score = 87
    view.on_key_press(arcade.key.SPACE, 0)
    assert view.score == 0
    assert not view.right_pressed
    assert not view.left_pressed
    assert not view.up_pressed

    view.right_pressed = False
    view.left_pressed = False
    view.up_pressed = False
    view.score = 10
    view.on_key_press(arcade.key.T, 0)
    assert not view.right_pressed
    assert not view.left_pressed
    assert not view.up_pressed
    assert view.score == 10

    arcade.close_window()

def test_on_key_release() -> None:
    arcade.open_window(800, 600, "Test Window")
    view = GameView()
    view.setup("maps/map3.txt")

    view.right_pressed = True
    view.left_pressed = True
    view.up_pressed = True
    view.on_key_release(arcade.key.RIGHT, 0)
    assert not view.right_pressed  
    assert view.left_pressed    
    assert view.up_pressed


    view.right_pressed = True
    view.on_key_release(arcade.key.LEFT, 0)
    assert not view.left_pressed
    assert view.right_pressed
    assert view.up_pressed


    view.left_pressed = True
    view.on_key_release(arcade.key.UP, 0)
    assert not view.up_pressed
    assert view.right_pressed
    assert view.left_pressed

    arcade.close_window()

def test_on_mouse_press() -> None:
    arcade.open_window(800, 600, "Test Window")
    view = GameView()
    view.setup("maps/map3.txt")

    initial_index = view.active_weapon_index
    initial_weapon = view.active_weapon_sprite

    view.on_mouse_press(x=100, y=100, button=arcade.MOUSE_BUTTON_RIGHT, modifiers=0)

    assert view.active_weapon_index == (initial_index + 1) % 2
    assert view.active_weapon_sprite != initial_weapon
    assert view.active_weapon_sprite == view.weapon[view.active_weapon_index]

    view.player_sprite.center_x = 300
    view.player_sprite.center_y = 300

    x_mouse = 400
    y_mouse = 350
    view.on_mouse_press(x=x_mouse, y=y_mouse, button=arcade.MOUSE_BUTTON_LEFT, modifiers=0)

    assert view.weapon_visible is True
    assert view.active_weapon_sprite in view.player_sprite_list

    assert view.active_weapon_sprite.center_y == view.player_sprite.center_y
    assert view.active_weapon_sprite.center_x > view.player_sprite.center_x

    if view.active_weapon_sprite == view.bow:
        assert view.arrow in view.player_sprite_list
        angle_rad = math.radians(view.arrow.angle)
        assert abs(view.arrow.change_x - 15 * math.cos(angle_rad)) < 1e-3
        assert abs(view.arrow.change_y - 15 * math.sin(angle_rad)) < 1e-3


    arcade.close_window()

def test_kill_monster () -> None:
    arcade.open_window(800, 600, "Test")
    view = GameView()
    view.setup("maps/map3.txt")

    monster1  = arcade.Sprite(center_x=300, center_y=300)
    view.Entities.append(monster1)

    view.sword.center_x = 300
    view.sword.center_y = 300

    assert monster1 in view.Entities
    view.kill_monster()
    assert monster1 not in view.Entities

    view.on_mouse_press(100, 100, arcade.MOUSE_BUTTON_RIGHT, 0)

    # Monstre 2 pour l'arc
    monster2 = arcade.Sprite(center_x=200, center_y=200)
    view.Entities.append(monster2)
    view.arrow.center_x = 200
    view.arrow.center_y = 200

    view.kill_monster()
    assert monster2 not in view.Entities

    monster3 = arcade.Sprite(center_x=1000, center_y=1000)
    view.Entities.append(monster3)

    view.sword.center_x = 0
    view.sword.center_y = 0
    view.arrow.center_x = 0
    view.arrow.center_y = 0

    view.kill_monster()
    assert monster3 in view.Entities

    arcade.close_window()






