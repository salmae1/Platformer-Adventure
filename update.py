import arcade
import math
from constants import ARROW_GRAVITY
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gameview2 import GameView2

def on_update(gameview: "GameView2", delta_time: float) -> None:
        """Called once per frame, before drawing.
        This is where in-world time "advances", or "ticks".
        """
        #update the physics engine
        gameview.physics_engine.update()

        if gameview.physics_engine.can_jump() :
            gameview.player.can_jump = True

        #updtate the camera to follow the player
        gameview.pan_camera_to_player()

        # Check for coins   
        if len(arcade.check_for_collision_with_list(gameview.player, gameview.coin_list)) != 0:
            coin = arcade.check_for_collision_with_list(gameview.player, gameview.coin_list)[0]
            coin.remove_from_sprite_lists()
            collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav", streaming=False)
            arcade.play_sound(collect_coin_sound, loop=False)
            gameview.score += 1
            
        #update the weapons
        gameview.player.weapon.update()

        # Update entities
        for entities in gameview.entity_list:
            entities.on_update(delta_time)
        
        #check for exit
        if gameview.exit_list:
            if math.dist((gameview.player.center_x, gameview.player.center_y),( gameview.exit_list[0].center_x, gameview.exit_list[0].center_y)) <= 64 :
                try :
                    next_level_sound = arcade.load_sound(":resources:/sounds/upgrade1.wav", streaming= False)
                    arcade.play_sound(next_level_sound, loop=False)
                    gameview.setup(gameview.next_map)
                except :
                    arcade.exit()

        #check for game over
        gameview.check_for_gameover()

        # Update all arrows in the sprite list
        arrows_to_remove: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()  # Track arrows to remove
        for arrow in gameview.player.sprite_list:
            if arrow != gameview.player and arrow not in gameview.player.weapon: # Ensure we only update arrows
                 # Check for collisions or if the arrow goes out of bounds
                if arrow.center_y > 0:
                    arrow.change_y -= ARROW_GRAVITY  # Apply gravity
                    if arcade.check_for_collision_with_list(arrow, gameview.wall_list):
                        # If the arrow hits a wall, remove it
                        arrows_to_remove.append(arrow) if arrow not in arrows_to_remove else None
                    elif arcade.check_for_collision_with_list(arrow, gameview.lava_list):
                        # If the arrow hits lava, remove it
                        arrows_to_remove.append(arrow) if arrow not in arrows_to_remove else None
                    elif arcade.check_for_collision_with_list(arrow, gameview.exit_list):
                        # If the arrow hits the exit, remove it
                        arrows_to_remove.append(arrow) if arrow not in arrows_to_remove else None
                    elif arcade.check_for_collision_with_list(arrow, gameview.platform_list):
                        # If the arrow hits a platform, remove it
                        arrows_to_remove.append(arrow) if arrow not in arrows_to_remove else None
                    if arcade.check_for_collision_with_list(arrow, gameview.entity_list):
                        # If the arrow hits an entity, remove it
                        hit_entity = arcade.check_for_collision_with_list(arrow, gameview.entity_list)[0]
                        hit_entity.remove_from_sprite_lists()
                        arrows_to_remove.append(arrow) if arrow not in arrows_to_remove else None
                    if arcade.check_for_collision_with_list(arrow, gameview.switch_list):
                        # If the arrow hits a switch, run the switch
                        hit_switch = arcade.check_for_collision_with_list(arrow, gameview.switch_list)[0]
                        gameview.run_switch(hit_switch)
                        arrows_to_remove.append(arrow) if arrow not in arrows_to_remove else None
                else:
                    arrows_to_remove.append(arrow)
                arrow.update()
                

        # Remove arrows marked for deletion
        if arrows_to_remove:
            for arrow in arrows_to_remove:
                arrow.remove_from_sprite_lists()
        
        # Make the weapon follow the player
        for weapon in gameview.player.weapon:
            if weapon in gameview.player.sprite_list:
                weapon.change_x = gameview.player.change_x
                weapon.change_y = gameview.player.change_y

        # Check for collisions with the sword
        if gameview.player.sword_draw_time is not None:
            time_since_drawn = time.time() - gameview.player.sword_draw_time
            if time_since_drawn <= 0.2:
                hit_with_sword = arcade.check_for_collision_with_list(
                    gameview.player.weapon[gameview.player.active_weapon_index],
                    gameview.entity_list
                )
                for monster in hit_with_sword:
                    monster.remove_from_sprite_lists()
                # Add cooldown for sword-switch collision
                now = time.time()
                if now - gameview._last_sword_switch_time > 0.25:
                    hit_sword_switch = arcade.check_for_collision_with_list(
                        gameview.player.weapon[gameview.player.active_weapon_index],
                        gameview.switch_list,
                        )
                    for switch in hit_sword_switch:
                        gameview.run_switch(switch)
                    gameview._last_sword_switch_time = now




