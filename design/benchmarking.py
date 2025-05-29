import time
import os
from typing import List
from maploader import MapLoader
from gameview import GameView
import arcade

def ensure_window() -> None:
    """Ensure an Arcade window exists before any Sprite/GameView operations."""
    try:
        window: arcade.Window | None = arcade.get_window()
        if window is None:
            raise Exception()
    except Exception:
        try:
            arcade.open_window(100, 100, "Benchmark Dummy Window", visible=False)
        except TypeError:
            arcade.open_window(100, 100, "Benchmark Dummy Window")

def write_map_file(filepath: str, yaml_header: str, map_body: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(yaml_header.strip() + "\n---\n" + map_body.lstrip("\n"))

def make_blocks_map(n_blocks: int, path: str) -> None:
    width: int = max(5, int(n_blocks**0.5))
    height: int = max(4, (n_blocks // width) + 3)
    yaml: str = f"""width: {width}
height: {height}
next-map: 
switches: []
gates: []
"""
    lines: List[str] = [" " * width for _ in range(height)]
    # Place player 'S' at the top left
    first_row: List[str] = list(lines[0])
    first_row[0] = "S"
    lines[0] = "".join(first_row)
    placed: int = 0
    for y in range(1, height-1):
        row: List[str] = list(lines[y])
        for x in range(width):
            if placed < n_blocks:
                row[x] = "="
                placed += 1
        lines[y] = "".join(row)
    map_body: str = "\n".join(lines)
    write_map_file(path, yaml, map_body)

def make_monster_map(n_mobs: int, path: str) -> None:
    width: int = max(10, min(n_mobs, 100))
    n_rows: int = (n_mobs // width) + 3
    height: int = max(4, n_rows)
    yaml: str = f"""width: {width}
height: {height}
next-map: 
switches: []
gates: []
"""
    lines: List[str] = [" " * width for _ in range(height)]
    # Place player 'S' at the top left
    first_row: List[str] = list(lines[0])
    first_row[0] = "S"
    lines[0] = "".join(first_row)
    mob_symbols: List[str] = ["o", "v", "G"]
    mob_idx: int = 0
    remaining: int = n_mobs
    for y in range(height-3, 0, -1):
        row: List[str] = list(lines[y])
        for x in range(width):
            if remaining > 0:
                row[x] = mob_symbols[mob_idx % 3]
                mob_idx += 1
                remaining -= 1
        lines[y] = "".join(row)
        if remaining <= 0:
            break
    # Add ground at the bottom
    lines[-1] = "=" * width
    map_body: str = "\n".join(lines)
    write_map_file(path, yaml, map_body)

def benchmark_level_loading(filepath: str, repeat: int = 3) -> float:
    times: List[float] = []
    for _ in range(repeat):
        start: float = time.time()
        loader: MapLoader = MapLoader(filepath)
        loader.read_map()
        times.append(time.time() - start)
    avg: float = sum(times) / repeat
    print(f"[{os.path.basename(filepath)}] Level loading: {avg:.6f} seconds (avg over {repeat} runs)")
    return avg

def benchmark_gameview_setup(filepath: str, repeat: int = 2) -> float:
    times: List[float] = []
    for _ in range(repeat):
        ensure_window()
        start: float = time.time()
        gv: GameView = GameView(filepath)
        times.append(time.time() - start)
    avg: float = sum(times) / repeat
    print(f"[{os.path.basename(filepath)}] GameView setup: {avg:.6f} seconds (avg over {repeat} runs)")
    return avg

def benchmark_on_update(filepath: str, n_frames: int = 30) -> float:
    ensure_window()
    gv: GameView = GameView(filepath)
    frame_times: List[float] = []
    for _ in range(n_frames):
        start: float = time.time()
        gv.on_update(1/60)
        frame_times.append(time.time() - start)
    avg: float = sum(frame_times) / n_frames
    print(f"[{os.path.basename(filepath)}] on_update: {avg*1000:.4f} ms/frame (avg over {n_frames} frames)")
    return avg

def run_benchmarks() -> None:
    sizes: List[int] = [1, 3, 5, 10, 50, 100, 500, 1000, 10000]
    maps_dir: str = "maps"
    os.makedirs(maps_dir, exist_ok=True)

    print("\n==== BENCHMARK: MapLoader (blocks) ====")
    for n in sizes:
        map_path  = os.path.join(maps_dir, "map99.txt")
        make_blocks_map(n, map_path)
        benchmark_level_loading(map_path, repeat=3)
        os.remove(map_path)

    print("\n==== BENCHMARK: MapLoader (monsters) ====")
    for n in sizes:
        map_path  = os.path.join(maps_dir, "map98.txt")
        make_monster_map(n, map_path)
        benchmark_level_loading(map_path, repeat=3)
        os.remove(map_path)

    print("\n==== BENCHMARK: GameView setup (blocks) ====")
    for n in sizes:
        map_path  = os.path.join(maps_dir, "map99.txt")
        make_blocks_map(n, map_path)
        benchmark_gameview_setup(map_path, repeat=2)
        os.remove(map_path)

    print("\n==== BENCHMARK: GameView setup (monsters) ====")
    for n in sizes:
        map_path  = os.path.join(maps_dir, "map98.txt")
        make_monster_map(n, map_path)
        benchmark_gameview_setup(map_path, repeat=2)
        os.remove(map_path)

    print("\n==== BENCHMARK: on_update (blocks) ====")
    for n in sizes:
        map_path = os.path.join(maps_dir, "map99.txt")
        make_blocks_map(n, map_path)
        benchmark_on_update(map_path, n_frames=30)
        os.remove(map_path)

    print("\n==== BENCHMARK: on_update (monsters) ====")
    for n in sizes:
        map_path = os.path.join(maps_dir, "map98.txt")
        make_monster_map(n, map_path)
        benchmark_on_update(map_path, n_frames=30)
        os.remove(map_path)

    # Remove the maps directory if empty
    try:
        if os.path.exists(maps_dir) and not os.listdir(maps_dir):
            os.rmdir(maps_dir)
    except Exception:
        pass

    try:
        arcade.close_window()
    except Exception:
        pass

if __name__ == "__main__":
    ensure_window()
    run_benchmarks()
