import json
import os

from collections import deque
from enviroment.object_type import ObjectType


SAVE_FILE = "save.json"


def save_world(world):

    ants_data = []
    for ant in world.ants:
        ants_data.append({
            "age": ant.age,
            "energy": ant.energy,
            "x": ant.x,
            "y": ant.y,
            "angle": ant.angle,

            "state": ant.state,

            "current_speed": ant.current_speed,
            "nest_timer": ant.nest_timer,
            "return_turn_timer": ant.return_turn_timer,
            "turn_timer": ant.turn_timer,

            "trail": list(ant.trail)
        })
    obstacles_data = []
    for obs in world.obstacles.obstacles:
        obstacles_data.append({
            "x": obs.x,
            "y": obs.y,
            "width": obs.width,
            "height": obs.height, 
            "type": obs.type.name
        })

    data = {
        "world_time": world.world_time,
        "ants": ants_data,
        "obstacles": obstacles_data
    }

    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_world(world):

    if not os.path.exists(SAVE_FILE):
        return

    with open(SAVE_FILE, "r") as f:
        data = json.load(f)

    world.world_time = data.get("world_time", 0)

    # cargar hormigas
    for ant, ant_data in zip(world.ants, data.get("ants", [])):

        ant.age = ant_data["age"]
        ant.energy = ant_data["energy"]
        ant.x = ant_data["x"]
        ant.y = ant_data["y"]
        ant.angle = ant_data["angle"]

        ant.state = ant_data.get("state", "Exploring")

        ant.current_speed = ant_data.get("current_speed", ant.speed)

        ant.nest_timer = ant_data.get("nest_timer", 0)
        ant.return_turn_timer = ant_data.get("return_turn_timer", 0)
        ant.turn_timer = ant_data.get("turn_timer", 0)

        ant.trail = deque(ant_data.get("trail", []), maxlen=20000)

    # cargar obstáculos
    world.obstacles.obstacles.clear()

    for obs_data in data.get("obstacles", []):
        world.obstacles.add_obstacle(
            obs_data["x"],
            obs_data["y"],
            obs_data["width"],
            obs_data["height"],
            ObjectType[obs_data["type"]]
        )

def reset_world(world):

    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)

    world.obstacles.obstacles.clear()