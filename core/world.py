import os

from agents.ant import Ant
from agents.ant_caste import AntCaste
from agents.nest import Nest
from core.save_system import save_world, load_world, reset_world
from enviroment.obstacle_manager import ObstacleManager
from enviroment.obstacle import Obstacle
from enviroment.pheromone import Pheromone


class World:

    def __init__(self, width_meters, height_meters):

        # Tamaño del mundo
        self.width_meters = width_meters
        self.height_meters = height_meters

        self.half_width = width_meters / 2
        self.half_height = height_meters / 2

        # Tiempo global
        self.world_time = 0.0

        # Objetos
        self.nest = Nest()
        self.obstacles = ObstacleManager()

        # Agentes
        self.ants = []
        self.pheromones = []

        # 👇 Crear 2 hormigas (Worker + Soldier)
        self.create_initial_ants()

        # Control
        self.paused = False

    # =========================
    # CREACIÓN DE AGENTES
    # =========================

    def create_initial_ants(self):
        worker = Ant(0, self, AntCaste.WORKER)
        soldier = Ant(1, self, AntCaste.SOLDIER)

        self.ants.append(worker)
        self.ants.append(soldier)

        self.ants.append(worker)
        self.ants.append(soldier)

    # =========================
    # UPDATE
    # =========================

    def update(self, dt):

        if self.paused:
            return

        self.world_time += dt

        for ant in self.ants:
            ant.update(dt, self)

        self.update_pheromones(dt)


    def update_pheromones(self, dt):

        for p in self.pheromones[:]:

            p.life -= dt

            if p.life <= 0:
                self.pheromones.remove(p)

    def add_pheromone(self, pheromone):
        self.pheromones.append(pheromone)
# =========================
    # DRAW
    # =========================

    def draw(self, screen, camera, show_trails=True, preview_data=None, panel=None, only_selected_trail=False, show_pheromones=True):
        self.nest.draw(screen, camera)
        self.obstacles.draw(screen, camera)


        # 🧪 FEROMONAS
        if show_pheromones:
            for p in self.pheromones:
                p.draw(screen, camera)

                
        selected_ant = panel.selected_ant if panel and panel.visible else None

        for ant in self.ants:

            # 🔹 decidir si dibujar trail
            if only_selected_trail:
                show_trail_for_ant = (
                    show_trails and
                    ant == selected_ant
                )
            else:
                show_trail_for_ant = show_trails

            # 🔹 saber si está seleccionada
            is_selected = (ant == selected_ant)

            ant.draw(
                screen,
                camera,
                show_trail_for_ant,
                is_selected=is_selected,
                only_selected_mode=only_selected_trail
            )

        # 👻 PREVIEW
        if preview_data is not None:
            x, y, width, height, obj_type = preview_data
            preview = Obstacle(x, y, width, height, obj_type)
            preview.draw_preview(screen, camera)

    # =========================
    # SAVE / LOAD
    # =========================

    def save_state(self):
        save_world(self)

    def load_state(self):
        load_world(self)

    # =========================
    # RESET
    # =========================

    def reset(self):

        reset_world()

        self.world_time = 0
        self.nest = Nest()

        self.ants.clear()

        # 👇 recrear correctamente
        self.create_initial_ants()