import json
import os

from collections import deque
from enviroment.object_type import ObjectType
from agents.ant_caste import AntCaste
from enviroment.pheromone import Pheromone


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
            "carrying_food": ant.carrying_food,

            "caste": ant.caste.name,

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
            "type": obs.type.name,
            "health": getattr(obs, "health", None)
        })

    pheromones_data = []
    for p in world.pheromones:
        pheromones_data.append({
            "x": p.x,
            "y": p.y,
            "type": p.type,
            "strength": p.max_strength,
            "life": p.life
        })

    data = {
        "world_time": world.world_time,
        "ants": ants_data,
        "obstacles": obstacles_data,
        "pheromones": pheromones_data
    }

    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)


def load_world(world):

    if not os.path.exists(SAVE_FILE):
        return

    with open(SAVE_FILE, "r") as f:
        data = json.load(f)

    world.world_time = data.get("world_time", 0)

    # -----------------------------
    # CARGAR HORMIGAS
    # -----------------------------
    for ant, ant_data in zip(world.ants, data.get("ants", [])):

        ant.age = ant_data["age"]
        ant.energy = ant_data["energy"]
        ant.x = ant_data["x"]
        ant.y = ant_data["y"]
        ant.angle = ant_data["angle"]

        saved_caste = ant_data.get("caste", "WORKER")
        ant.caste = AntCaste[saved_caste]
        ant.apply_caste_stats()

        saved_state = ant_data.get("state", "Exploring")
        states_need_target = ["GoingToFood", "Attacking"]

        if saved_state in states_need_target:
            ant.state = "Exploring"
            ant.target = None
        else:
            ant.state = saved_state
            ant.target = None

        ant.is_eating = False
        ant.carrying_food = ant_data.get("carrying_food", False)

        ant.nest_timer = ant_data.get("nest_timer", 0)
        ant.return_turn_timer = ant_data.get("return_turn_timer", 0)
        ant.turn_timer = ant_data.get("turn_timer", 0)

        ant.trail = deque(ant_data.get("trail", []), maxlen=20000)

    # -----------------------------
    # OBSTÁCULOS
    # -----------------------------
    world.obstacles.obstacles.clear()

    for obs_data in data.get("obstacles", []):
        obj = world.obstacles.add_obstacle(
            obs_data["x"],
            obs_data["y"],
            obs_data["width"],
            obs_data["height"],
            ObjectType[obs_data["type"]]
        )

        if "health" in obs_data and obs_data["health"] is not None:
            obj.health = obs_data["health"]

    # -----------------------------
    # FEROMONAS
    # -----------------------------
    world.pheromones.clear()

    for p_data in data.get("pheromones", []):
        p = Pheromone(
            p_data["x"],
            p_data["y"],
            p_data["type"],
            strength=p_data["strength"],
            life=p_data["life"]
        )
        world.pheromones.append(p)


def reset_world(world):

    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)

    world.obstacles.obstacles.clear()
    world.pheromones.clear()