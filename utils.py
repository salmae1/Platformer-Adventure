from enum import Enum
from typing import List, Dict, Optional
from constants import tile_size, Arrow ,ASSETS ,Platform
def coordinate(x: float) -> float:
    """Convert tile coordinates to pixel coordinates."""
    return x * tile_size + tile_size // 2

def bfs_connected_components(start_x: int, start_y: int, map_data : list[str]) -> tuple[int,int,list[tuple[int, int]]]:
            """Find connected components using BFS."""
            height = len(map_data)
            width = len(map_data[0]) if height > 0 else 0
            # Initialize the list to store connected components
            connected_components = []
            if  map_data[start_y][start_x]  in ASSETS and map_data[start_y][start_x] not in {"^","*", "S","|","p","E"}:
                # Initialize BFS
                queue = [(start_x, start_y)]
                visit = {(start_x, start_y)}
                while queue:
                    x, y = queue.pop(0)
                    connected_components.append((x, y))
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        new_x = x + dx
                        new_y = y + dy
                    # Correct bounds check
                        if 0 <= new_y < len(map_data) and 0 <= new_x < len(map_data[new_y]):
                            if (0 <= new_y < len(map_data)) and (0 <= new_x < len(map_data[new_y])) \
                                and map_data[new_y][new_x] in ASSETS and (new_x, new_y) not in visit \
                                and map_data[new_y][new_x] not in {"^","*", "S","|","p","E"}:
                                queue.append((new_x, new_y))
                                visit.add((new_x, new_y))
                        else :
                            continue
            return width,height,connected_components


def get_platform(start_x: int, start_y: int, map_data: list[str]) -> Platform:
            """Get the platform and its bounds."""
            width,height,connected_components= bfs_connected_components(start_x, start_y, map_data)
            # Initialize bounds
            NO_LEFT_BOUNDS = width 
            NO_RIGHT_BOUNDS = 0
            NO_UP_BOUNDS = 0
            NO_DOWN_BOUNDS = height 
            #create a dictionary to store the bounds
            Bounds: dict[Arrow, int] = {
                    Arrow.LEFT: NO_LEFT_BOUNDS,
                    Arrow.RIGHT: NO_RIGHT_BOUNDS,
                    Arrow.UP: NO_UP_BOUNDS,
                    Arrow.DOWN: NO_DOWN_BOUNDS
                }
            # Iterate through the connected components
            for coordinates in connected_components:

                x,y = coordinates
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    new_x = x + dx
                    new_y = y + dy

                    if 0 <= new_y < len(map_data) and 0 <= new_x < len(map_data[new_y]):
                         
                         # Check for a serie of arrows in the left direction
                         if map_data[new_y][new_x] == "←" and dx == -1:
                              #update the bounds
                              check_limit_l = new_x
                              while check_limit_l>= 0 and map_data[new_y][check_limit_l] == "←" :
                                   #Iterate through the serie of arrows
                                   Bounds[Arrow.LEFT] = min(Bounds[Arrow.LEFT], check_limit_l )
                                   check_limit_l -= 1
                         
                            # Check for a serie of arrows in the right direction
                         if map_data[new_y][new_x] == "→" and dx == 1:
                              #update the bounds
                              check_limit_r = new_x
                              while check_limit_r< width and map_data[new_y][check_limit_r] == "→":
                                   #Iterate through the serie of arrows
                                   Bounds[Arrow.RIGHT] = max(Bounds[Arrow.RIGHT], check_limit_r )
                                   check_limit_r +=1

                         
                         # Check for a serie of arrows in the up direction
                         if map_data[new_y][new_x] == "↑" and dy == 1:
                                #update the bounds
                              check_limit_u = new_y
                              while check_limit_u < height and map_data[check_limit_u][new_x] == "↑":
                                   #Iterate through the serie of arrows
                                   Bounds[Arrow.UP] = max(Bounds[Arrow.UP], check_limit_u )
                                   check_limit_u += 1
                         
                         # Check for a serie of arrows in the down direction
                         if map_data[new_y][new_x] == "↓" and dy == -1:
                                #update the bounds
                              check_limit_d = new_y
                              while check_limit_d>= 0 and map_data[check_limit_d][new_x] == "↓":
                                   #Iterate through the serie of arrows
                                   Bounds[Arrow.DOWN] = min(Bounds[Arrow.DOWN], check_limit_d )
                                   check_limit_d -= 1

            return Platform(connected_components, Bounds)

def get_borders(block: list[tuple[int, int]]) -> tuple[int,int,int,int]:
    """Get the borders of the platform."""
    if block :
        left = min(x for x, y in block)
        right = max(x for x, y in block)
        up = max(y for x, y in block)
        down = min(y for x, y in block)
        return left, right, up, down
    else:
        return 0, 0, 0, 0
