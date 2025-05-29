import os
from typing import List, Dict, Any
from maploader import MapLoader

def write_test_map(filepath: str, content: str) -> None:
    """Utility to write content to a file, creating directories as needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def test_map_loader_all_cases() -> None:
    test_dir: str = "maps"

    # 1. Basic valid map
    map1_path: str = os.path.join(test_dir, "map10.txt")
    map1_content: str = """width: 5
height: 3
next-map: map2.txt
switches:
  - x: 1
    y: 2
    state: on
    switch_on:
      - x: 2
        y: 2
        action: open-gate
    switch_off:
      - x: 2
        y: 2
        action: close-gate
gates:
  - x: 2
    y: 2
    state: closed
---
     
 S   
==£==
"""

    # 2. Map with blank lines & whitespace
    map2_path: str = os.path.join(test_dir, "map11.txt")
    map2_content: str = """width: 4
height: 4
next-map: map3.txt
switches: []
gates: []
---
    
  S 
    
==£=
---    
"""

    # 3. Map with no switches or gates
    map3_path: str = os.path.join(test_dir, "map12.txt")
    map3_content: str = """width: 2
height: 2
next-map: map4.txt
---
 S
==
"""

    # 4. Map with state as boolean (should convert to "on")
    map4_path: str = os.path.join(test_dir, "map13.txt")
    map4_content: str = """width: 2
height: 2
next-map: map5.txt
switches:
  - x: 0
    y: 1
    state: true
    switch_on: []
    switch_off: []
gates: []
---
 S
==
"""

    # 5. Map with "disable" action
    map5_path: str = os.path.join(test_dir, "map14.txt")
    map5_content: str = """width: 2
height: 2
next-map: map6.txt
switches:
  - x: 1
    y: 1
    state: off
    switch_on:
      - action: disable
    switch_off: []
gates: []
---
 S
==
"""

    # 6. Map with missing separator (should raise ValueError)
    map6_path: str = os.path.join(test_dir, "map15.txt")
    map6_content: str = """width: 2
height: 2
next-map: map7.txt
 S
==
"""

    # 7. Map with extra separator at bottom (should ignore lines after 2nd ---)
    map7_path: str = os.path.join(test_dir, "map16.txt")
    map7_content: str = """width: 3
height: 2
next-map: map8.txt
switches: []
gates: []
---
 A 
 B 
---
ignore this line
"""

    # Write all test maps
    write_test_map(map1_path, map1_content)
    write_test_map(map2_path, map2_content)
    write_test_map(map3_path, map3_content)
    write_test_map(map4_path, map4_content)
    write_test_map(map5_path, map5_content)
    write_test_map(map6_path, map6_content)
    write_test_map(map7_path, map7_content)

    try:
        # Test 1: Basic map
        loader: MapLoader = MapLoader(map1_path)
        width, height, map_data, next_map, switches, gates = loader.read_map()
        assert width == 5
        assert height == 3
        assert next_map == "maps/map2.txt"
        # The bottom of the map is the last map line before EOF or 2nd --- (here: "==£==")
        assert map_data == [
            "==£==",
            " S   ",
            "     "
        ]
        assert switches[0]["x"] == 1 and switches[0]["y"] == 2
        assert switches[0]["state"] == "on"
        assert gates[0]["x"] == 2 and gates[0]["state"] == "closed"

        # Test 2: Map with blank lines and whitespace
        loader = MapLoader(map2_path)
        width, height, map_data, next_map, switches, gates = loader.read_map()
        assert width == 4
        assert height == 4
        assert map_data == [
            "==£=",
            "    ",
            "  S ",
            "    ",
        ]
        assert switches == []
        assert gates == []
        assert next_map == "maps/map3.txt"

        # Test 3: Map with no switches or gates
        loader = MapLoader(map3_path)
        width, height, map_data, next_map, switches, gates = loader.read_map()
        assert width == 2
        assert height == 2
        assert switches == []
        assert gates == []
        assert map_data == [
            "==",
            " S"
        ]
        assert next_map == "maps/map4.txt"

        # Test 4: Map with boolean switch state
        loader = MapLoader(map4_path)
        width, height, map_data, next_map, switches, gates = loader.read_map()
        assert switches[0]["state"] == "on"

        # Test 5: Map with disable action
        loader = MapLoader(map5_path)
        width, height, map_data, next_map, switches, gates = loader.read_map()
        assert switches[0]["switch_on"][0]["action"] == "disable"
        assert switches[0]["switch_on"][0]["x"] == 1 and switches[0]["switch_on"][0]["y"] == 1

        # Test 6: Map missing separator (should raise ValueError)
        loader = MapLoader(map6_path)
        raised: bool = False
        try:
            loader.read_map()
        except ValueError:
            raised = True
        assert raised, "Missing separator should raise ValueError"

        # Test 7: Map with extra separator at bottom (component: lines after 2nd --- ignored)
        loader = MapLoader(map7_path)
        width, height, map_data, next_map, switches, gates = loader.read_map()
        # The two map lines just before the 2nd '---' are reversed
        assert map_data == [
            " B ",
            " A "
        ]
        assert width == 3
        assert height == 2


    finally:
        # Clean up all test files and directory
        for path in [map1_path, map2_path, map3_path, map4_path, map5_path, map6_path, map7_path]:
            if os.path.exists(path):
                os.remove(path)
        if os.path.exists(test_dir) and not os.listdir(test_dir):
            os.rmdir(test_dir)