import json
import os

from agents.ant import Ant
from agents.nest import Nest


class World:
    def __init__(self, width_meters, height_meters):
        self.width_meters = width_meters
        self.height_meters = height_meters

        self.world_time = 0.0  # Tiempo en segundos desde que nació el mundo

        self.half_width = width_meters / 2
        self.half_height = height_meters / 2

        self.nest = Nest()

        self.ants = []
        self.create_initial_ant()

        self.paused = False

    def create_initial_ant(self):
        ant = Ant(1, self)
        self.ants.append(ant)

    def update(self, dt):
        if self.paused:
            return  # ⛔ No actualizar nada

        self.world_time += dt

        for ant in self.ants:
            ant.update(dt, self)


    def draw(self, screen, camera):
        self.nest.draw(screen, camera)

        for ant in self.ants:
            ant.draw(screen, camera)

    def save_state(self):
        ant = self.ants[0]

        data = {
            "age": ant.age,
            "energy": ant.energy,
            "x": ant.x,
            "y": ant.y,
            "angle": ant.angle,
            "world_time": self.world_time
        }

        with open("save.json", "w") as f:
            json.dump(data, f)

    def load_state(self):

        if not os.path.exists("save.json"):
            return

        if os.path.getsize("save.json") == 0:
            return

        with open("save.json", "r") as f:
            data = json.load(f)

        ant = self.ants[0]

        ant.age = data["age"]
        ant.energy = data["energy"]
        ant.x = data["x"]
        ant.y = data["y"]
        ant.angle = data["angle"]
        self.world_time = data.get("world_time", 0.0)

    def reset(self):
        if os.path.exists("save.json"):
            os.remove("save.json")

        self.nest = Nest()
        self.ants.clear()
        self.create_initial_ant()