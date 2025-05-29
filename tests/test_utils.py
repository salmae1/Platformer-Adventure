import os
from maploader import MapLoader
from utils import bfs_connected_components, get_platform, get_borders
from constants import Arrow

def write_map_file(filepath: str, yaml_header: str, map_body: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(yaml_header.strip() + "\n---\n" + map_body)

def test_utils_platforms() -> None:
    test_dir: str = "maps"

    # 1. Horizontal platform moving right
    map1_path = os.path.join(test_dir, "map51.txt")
    yaml_1 = """width: 13
height: 4
next-map: map2.txt
switches: []
gates: []
"""
    # Platform at (0,3),(1,3),(2,3), arrows at (3,3)-(7,3)
    map1_body = """
---→→→→→
 S    E  
===---===
=======
"""

    # 2. Horizontal platform moving left (starts right)
    map2_path = os.path.join(test_dir, "map52.txt")
    yaml_2 = yaml_1
    # Platform at (7,3),(8,3),(9,3), arrows at (2,3)-(6,3)
    map2_body = """
  ←←←←←--- 
 S    E  
===---====
=======
"""

    # 3. Bidirectional arrows, platform starts left, arrows left/right
    map3_path = os.path.join(test_dir, "map53.txt")
    yaml_3 = """width: 14
height: 4
next-map: map2.txt
switches: []
gates: []
"""
    # Platform at (3,3),(4,3),(5,3), left arrows at (0,3)-(2,3), right at (6,3)-(8,3)
    map3_body = """
←←←---→→→
 S     E   
===---====
==========
"""

    # 4. Vertical platform, arrows up and down (but only =, -, x, £ can be platforms)
    # | is NOT a platform and should not be included
    map4_path = os.path.join(test_dir, "map54.txt")
    yaml_4 = """width: 8
height: 7
next-map: map2.txt
switches: []
gates: []
"""
    # Platform up and down
    map4_body = """
   ↑   
   ↑   
   -   
   -   
   =   
   =   
   ↓   
"""

    # 5. Nontrivial block, diagonal not connected
    map5_path = os.path.join(test_dir, "map55.txt")
    yaml_5 = """width: 16
height: 8
next-map: map2.txt
switches: []
gates: []
"""
    map5_body = """
  -   ---
    xxx
    x  ---→→→
←←--- 
 S        E
===---========
==============
"""

    # 6. Two platforms that will touch each other at the same position (arrows touch)
    map6_path = os.path.join(test_dir, "map56.txt")
    yaml_6 = """width: 18
height: 5
next-map: map2.txt
switches: []
gates: []
"""
    
    map6_body = """
---→→→→→→→←←←←←←--
                   
                   
 S        E        
==================
"""

    # Write test maps
    write_map_file(map1_path, yaml_1, map1_body)
    write_map_file(map2_path, yaml_2, map2_body)
    write_map_file(map3_path, yaml_3, map3_body)
    write_map_file(map4_path, yaml_4, map4_body)
    write_map_file(map5_path, yaml_5, map5_body)
    write_map_file(map6_path, yaml_6, map6_body)

    try:
        # 1. Horizontal platform, arrows right: only - are platforms
        loader = MapLoader(map1_path)
        _, _, map_data, _, _, _ = loader.read_map()
        width, height, block = bfs_connected_components(0, 3, map_data)
        assert sorted(block) == [(0,3), (1,3), (2,3)]
        plat = get_platform(0,3,map_data)
        assert sorted(plat.block) == [(0,3), (1,3), (2,3)]
        # Should detect right bound at 7 (rightmost →)
        assert plat.bound_right == 7
        # Not affected by left arrows, so stays at width
        assert plat.bound_left == width

        # 2. Horizontal platform, arrows left
        loader = MapLoader(map2_path)
        _, _, map_data, _, _, _ = loader.read_map()
        width, height, block = bfs_connected_components(7, 3, map_data)
        assert sorted(block) == [(7,3), (8,3), (9,3)]
        plat = get_platform(7,3,map_data)
        assert plat.bound_left == 2
        assert plat.bound_right == 0

        # 3. Bidirectional arrows
        loader = MapLoader(map3_path)
        _, _, map_data, _, _, _ = loader.read_map()
        plat = get_platform(3, 3, map_data)
        assert plat.bound_left == 0
        assert plat.bound_right == 8

        # 4. Vertical platforms using only -, = (not |)
        loader = MapLoader(map4_path)
        _, _, map_data, _, _, _ = loader.read_map()
        width, height, block1 = bfs_connected_components(3,2,map_data)
        width, height, block2 = bfs_connected_components(3,4,map_data)
        # block1: (3,2), (3,3) are -
        assert sorted(block1) == [(3,1),(3,2), (3,3),(3,4)]
        assert sorted(block2) == sorted(block1)  # same block
        plat = get_platform(3,2,map_data)
        # For plat1 (the -), check vertical bounds
        assert plat.bound_up == 6  # upmost arrow at y=6
        assert plat.bound_down == 0 # downmost arrow at y=0
        # 5. Nontrivial block
        loader = MapLoader(map5_path)
        _, _, map_data, _, _, _ = loader.read_map()
        width, height, block = bfs_connected_components(3,3,map_data)
        assert  (7,6) in block and (2,6) not in block

        # 6. Two platforms that will touch each other at their bounds (arrows touch)
        loader = MapLoader(map6_path)
        _, _, map_data, _, _, _ = loader.read_map()
        # Left platform: (0,4),(1,4),(2,4); right platform: (16,4),(17,4)
        w, h, block_left = bfs_connected_components(0,4,map_data)
        w, h, block_right = bfs_connected_components(17,4,map_data)
        assert sorted(block_left) == [(0,4),(1,4),(2,4)]
        assert sorted(block_right) == [(16,4),(17,4)]
        plat_left = get_platform(0,4,map_data)
        plat_right = get_platform(15,4,map_data)
        # Check their bounds: left platform should move right up to 8, right platform should move left down to 9
        assert plat_left.bound_right == 9
        assert plat_left.bound_left == w
        assert plat_right.bound_left == 18
        assert plat_right.bound_right == 0

    finally:
        # Cleanup
        for path in [map1_path, map2_path, map3_path, map4_path, map5_path, map6_path]:
            if os.path.exists(path):
                os.remove(path)
        if os.path.exists(test_dir) and not os.listdir(test_dir):
            os.rmdir(test_dir)