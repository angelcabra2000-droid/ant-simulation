import os
import random
import math

from agents.ant import Ant
from agents.ant_caste import AntCaste
from agents.nest import Nest
from core.save_system import save_world, load_world, reset_world
from enviroment.obstacle_manager import ObstacleManager
from enviroment.obstacle import Obstacle


class World:

    def __init__(self, width_meters, height_meters):

        self.width_meters = width_meters
        self.height_meters = height_meters

        self.half_width = width_meters / 2
        self.half_height = height_meters / 2

        self.world_time = 0.0
        self.paused = False

        # =========================
        # ENTORNO
        # =========================
        self.nest = Nest()
        self.obstacles = ObstacleManager()

        self.ants = []
        self.pheromones = []

        # =========================
        # CONFIGURACIÓN DE COLONIA
        # =========================
        self.next_ant_id = 0

        self.max_ants = 100
        self.worker_ratio = 0.85

        self.target_workers = int(self.max_ants * self.worker_ratio)
        self.target_soldiers = self.max_ants - self.target_workers

        # Spawn progresivo
        self.spawn_timer = 0.0
        self.spawn_interval = 0.15

    # =========================
    # CREACIÓN DE AGENTES
    # =========================

    def create_ant(self, caste):
        """Crea una hormiga cerca de la salida del nido."""
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, 0.03)

        x = self.nest.x + math.cos(angle) * distance
        y = self.nest.y + math.sin(angle) * distance

        ant = Ant(self.next_ant_id, self, caste, x=x, y=y)

        self.ants.append(ant)
        self.next_ant_id += 1

        return ant

    def create_initial_ants(self):
        """Crea una pequeña colonia inicial."""
        self.create_ant(AntCaste.WORKER)
        self.create_ant(AntCaste.SOLDIER)

    def spawn_ant_if_needed(self):
        """Genera hormigas gradualmente hasta alcanzar el límite."""
        if len(self.ants) >= self.max_ants:
            return

        workers = sum(1 for ant in self.ants if ant.caste == AntCaste.WORKER)
        soldiers = sum(1 for ant in self.ants if ant.caste == AntCaste.SOLDIER)

        # Mantener la proporción durante el crecimiento
        worker_progress = workers / self.target_workers if self.target_workers else 1
        soldier_progress = soldiers / self.target_soldiers if self.target_soldiers else 1

        if worker_progress <= soldier_progress:
            if workers < self.target_workers:
                self.create_ant(AntCaste.WORKER)
        else:
            if soldiers < self.target_soldiers:
                self.create_ant(AntCaste.SOLDIER)

    # =========================
    # UPDATE
    # =========================

    def update(self, dt):

        if self.paused:
            return

        self.world_time += dt

        # Spawn progresivo
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_ant_if_needed()
            self.spawn_timer = 0.0

        # Actualizar hormigas
        for ant in self.ants[:]:
            ant.update(dt, self)

        # Actualizar feromonas
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

    def draw(
        self,
        screen,
        camera,
        show_trails=True,
        preview_data=None,
        panel=None,
        only_selected_trail=False,
        show_pheromones=True
    ):
        self.nest.draw(screen, camera)
        self.obstacles.draw(screen, camera)

        if show_pheromones:
            for p in self.pheromones:
                p.draw(screen, camera)

        selected_ant = panel.selected_ant if panel and panel.visible else None

        for ant in self.ants:

            if only_selected_trail:
                show_trail_for_ant = show_trails and (ant == selected_ant)
            else:
                show_trail_for_ant = show_trails

            is_selected = (ant == selected_ant)

            ant.draw(
                screen,
                camera,
                show_trail_for_ant,
                is_selected=is_selected,
                only_selected_mode=only_selected_trail
            )

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
        reset_world(self)

        self.world_time = 0.0
        self.nest = Nest()

        self.ants.clear()
        self.pheromones.clear()

        self.next_ant_id = 0
        self.spawn_timer = 0.0

        self.create_initial_ants()