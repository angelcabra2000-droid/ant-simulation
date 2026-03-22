import random
import math
import pygame
from collections import deque

from config.settings import ANT_COLOR
#from agents.ant_behavior import AntBehavior
from agents.worker_behavior import WorkerBehavior
from agents.soldier_behavior import SoldierBehavior
from agents.ant_caste import AntCaste

class Ant:

    def __init__(self, ant_id, world):

        self.id = ant_id
        self.world = world
        self.caste = None

        # -------------------
        # VIDA
        # -------------------
        self.age = 0
        self.energy = 100

        # -------------------
        # ESTADO
        # -------------------

        self.state = "Exploring"
        self.carrying_food = False
        self.target = None

        # -------------------
        # POSICIÓN
        # -------------------

        self.x = random.uniform(-1, 1)
        self.y = random.uniform(-1, 1)

        # -------------------
        # MOVIMIENTO
        # -------------------

        self.angle = random.uniform(0, 2 * math.pi)
        self.turn_speed = 3
        self.speed = 0.0
        self.current_speed = 0.0

        # -------------------
        # PERCEPCIÓN
        # -------------------

        self.vision_radius = 0.5
        self.fov = math.pi / 2

        # -------------------
        # EXPLORACIÓN
        # -------------------

        self.turn_timer = 0
        self.turn_interval = random.uniform(0.5, 2)

        # -------------------
        # RETORNO AL NIDO
        # -------------------

        self.return_turn_timer = 0
        self.return_turn_interval = random.uniform(0.2, 0.6)

        # -------------------
        # ESPERA EN EL NIDO
        # -------------------

        self.nest_wait_time = 10
        self.nest_timer = 0

        # -------------------
        # TRAIL
        # -------------------

        self.trail = deque(maxlen=2000)
        self.trail_timer = 0
        self.trail_interval = 1

        # -------------------
        # TIEMPO COMIENDO
        # -------------------

        self.eating_timer = 0
        self.eating_time = 3
        self.is_eating = False

        if self.caste is not None:
            self.apply_caste_stats()

    # ---------------------------------


    def update(self, dt, world):

        if self.caste == AntCaste.WORKER:
            WorkerBehavior.update(self, dt, world)

        elif self.caste == AntCaste.SOLDIER:
            SoldierBehavior.update(self, dt, world)

        self.trail.append((self.x, self.y))

    # ---------------------------------

    def draw(self, screen, camera, show_trail=True):

        # ---- TRAIL ----
        if show_trail and len(self.trail) > 10:

            points = []
            trail_to_draw = list(self.trail)[-1000:]

            for x, y in trail_to_draw:
                points.append(camera.world_to_screen(x, y))

            pygame.draw.lines(screen, (180, 180, 180), False, points, 2)

        
        # ---- POSICIÓN EN PANTALLA ----
        screen_pos = camera.world_to_screen(self.x, self.y)

        radius_pixels = self.radius * camera.pixels_per_meter * camera.zoom
        radius_pixels = max(int(radius_pixels), 1)

        # ---- COLOR SEGÚN CASTA ----
        if self.caste == AntCaste.WORKER:
            color = (0, 200, 0)

        elif self.caste == AntCaste.SOLDIER:
            color = (200, 50, 50)

        else:
            color = (180, 180, 180)  # fallback

        pygame.draw.circle(screen, color, screen_pos, radius_pixels)
        # ---- COMIDA QUE CARGA ----
        if self.state == "ReturningFood":

            food_offset = radius_pixels * 1.5

            food_x = screen_pos[0] + math.cos(self.angle) * food_offset
            food_y = screen_pos[1] + math.sin(self.angle) * food_offset

            food_radius = max(2, radius_pixels // 2)

            pygame.draw.circle(screen, (0, 220, 0), (int(food_x), int(food_y)), food_radius)

    def apply_caste_stats(self):
        if self.caste == AntCaste.WORKER:
            self.radius = 0.008
            self.speed = 0.09
        elif self.caste == AntCaste.SOLDIER:
            self.radius = 0.012
            self.speed = 0.06

        self.current_speed = self.speed