import yaml
from typing import TypedDict, Literal, List , Final
import re
from constants import Arrow , ASSETS
class ACTION(TypedDict):
    x: int
    y: int
    action: Literal["open-gate", "close-gate", "disable"]

class SWITCH(TypedDict, total = False):
    x: int
    y: int
    state: Literal["on", "off"]
    switch_on: list[ACTION]
    switch_off: list[ACTION]
    enabled: bool

class GATE(TypedDict, total = False):
    x: int
    y: int
    state: Literal["open", "closed"]
    
class MapLoader:
    __filepath : str 

    def __init__(self, filepath: str = "maps/map1.txt") -> None:
        """Initialize the MapLoader with a file path."""
        self.__filepath = filepath

    def read_map(self) -> tuple[int, int, list[str], str, list[SWITCH], list[GATE]] :
        """read and analyse the map."""

        with open(self.__filepath, 'r', encoding="utf-8", newline='\n') as f:
            lines =f.readlines()

        sep_index = None
        for idx, line in enumerate(lines):
            if line.strip() == "---":
                sep_index = idx
                break

        if sep_index is None:
            raise ValueError("No map separator '---' found in file")
        
        yaml_text = "".join (lines[:sep_index])
        config  = yaml.safe_load(yaml_text)
        # Configuration
        width : int = config.get("width",0)
        height : int = config.get("height",0)
        next_map : str = config.get("next-map"," ")
        next_map = "maps/" + next_map
        switches_ = config.get("switches", [])
        gates = config.get("gates", [])

        switches : list[SWITCH] = []
        for yaml_switch in switches_:
            x = int(yaml_switch["x"])
            y = int(yaml_switch["y"])
            state = yaml_switch.get("state", "off")
            # Correct: use the YAML state if present, otherwise default to "off"
            if state is True:
                state = "on"
            # Ensure state is always a string and not None
            state = str(state)

            switch_on: list[ACTION] = []
            for action in yaml_switch.get("switch_on", []):
                if action["action"] == "disable":
                    switch_on.append({"x": x, "y": y, "action": "disable"})  # ← coordonnées du switch
                else:
                    switch_on.append({
                        "x": int(action["x"]),
                        "y": int(action["y"]),
                        "action": action["action"],
                    })

            switch_off: list[ACTION] = []
            for action in yaml_switch.get("switch_off", []):
                if action["action"] == "disable":
                    switch_off.append({"x": x, "y": y, "action": "disable"})  # ← coordonnées du switch
                else:
                    switch_off.append({
                        "x": int(action["x"]),
                        "y": int(action["y"]),
                        "action": action["action"],
                    })

            switches.append({
                "x": x,
                "y": y,
                "state": state,  # This will now correctly be "on" if set in YAML
                "switch_on": switch_on,
                "switch_off": switch_off,
                "enabled": True,
            })

        idx += 1
        map_data : list[str]= []

        # Characters
        while idx < len(lines)  and lines[idx].rstrip() != "---":
            lines[idx] = lines[idx].rstrip().ljust(width)
            map_data.append(lines[idx])
            idx += 1
                   
        map_data = list(reversed(map_data))
        return width, height, map_data, next_map, switches, gates
    
    @property
    def filepath(self) -> str:
        """Get the file path."""
        return self.__filepath
    
    @filepath.setter
    def filepath(self, filepath: str) -> None:
        """Set the file path."""
        path = re.compile(r"maps/+map[0-9]+\.txt")
        if path.match(filepath):
            self.__filepath = filepath
        else:
            raise ValueError("Invalid file path. Must be in the format maps/mapX.txt")

        





