import json
import os
from collections import deque


SAVE_FILE = "save.json"


def save_world(world):

    ants_data = []

    for ant in world.ants:
        ant_data = {
            "id": ant.id,
            "age": ant.age,
            "energy": ant.energy,
            "x": ant.x,
            "y": ant.y,
            "angle": ant.angle,
            "trail": list(ant.trail)  # deque -> list
        }

        ants_data.append(ant_data)

    data = {
        "world_time": world.world_time,
        "ants": ants_data
    }

    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)


def load_world(world):

    if not os.path.exists(SAVE_FILE):
        return

    if os.path.getsize(SAVE_FILE) == 0:
        return

    with open(SAVE_FILE, "r") as f:
        data = json.load(f)

    world.world_time = data.get("world_time", 0)

    ants_data = data.get("ants", [])

    for i, ant_data in enumerate(ants_data):

        if i >= len(world.ants):
            break

        ant = world.ants[i]

        ant.age = ant_data["age"]
        ant.energy = ant_data["energy"]
        ant.x = ant_data["x"]
        ant.y = ant_data["y"]
        ant.angle = ant_data["angle"]

        ant.trail = deque(ant_data.get("trail", []), maxlen=20000)


def reset_world():

    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)