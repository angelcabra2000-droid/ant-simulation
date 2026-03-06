import os

from agents.ant import Ant
from agents.nest import Nest
from core.save_system import save_world, load_world, reset_world
from enviroment.obstacle_manager import ObstacleManager

class World:

    def __init__(self, width_meters, height_meters):

        # Tamaño del mundo
        self.width_meters = width_meters
        self.height_meters = height_meters

        self.half_width = width_meters / 2
        self.half_height = height_meters / 2

        # Tiempo global del mundo
        self.world_time = 0.0

        # Objetos del mundo
        self.nest = Nest()
        self.obstacles = ObstacleManager()

        # Agentes
        self.ants = []

        # Crear primera hormiga
        self.create_initial_ant()

        # Control simulación
        self.paused = False

    # =========================
    # CREACIÓN DE AGENTES
    # =========================

    def create_initial_ant(self):

        ant = Ant(1, self)
        self.ants.append(ant)

    # =========================
    # UPDATE DEL MUNDO
    # =========================

    def update(self, dt):

        if self.paused:
            return

        self.world_time += dt

        for ant in self.ants:
            ant.update(dt, self)

    # =========================
    # RENDER
    # =========================

    def draw(self, screen, camera, show_trails=True):

        self.nest.draw(screen, camera)

        self.obstacles.draw(screen, camera)

        for ant in self.ants:
            ant.draw(screen, camera, show_trails)

    # =========================
    # SISTEMA DE GUARDADO
    # =========================

    def save_state(self):

        save_world(self)

    def load_state(self):

        load_world(self)

    # =========================
    # RESET DEL MUNDO
    # =========================

    def reset(self):

        reset_world()

        self.world_time = 0

        self.nest = Nest()

        self.ants.clear()

        self.create_initial_ant()