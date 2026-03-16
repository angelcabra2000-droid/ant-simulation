import random
import math
import pygame
from collections import deque

from config.settings import ANT_COLOR
from agents.ant_behavior import AntBehavior


class Ant:

    def __init__(self, ant_id, world):

        self.id = ant_id
        self.world = world

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
        self.speed = 0.07
        self.turn_speed = 3
        self.current_speed = self.speed

        # -------------------
        # PERCEPCIÓN
        # -------------------

        self.vision_radius = 0.5
        self.fov = math.pi / 2

        # -------------------
        # CUERPO
        # -------------------

        self.radius = 0.004

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

    # ---------------------------------

    def update(self, dt, world):
        AntBehavior.update(self, dt, world)

    # ---------------------------------

    def draw(self, screen, camera, show_trail=True):

        # ---- TRAIL ----
        if show_trail and len(self.trail) > 1:

            points = []
            trail_to_draw = list(self.trail)[-1000:]

            for x, y in trail_to_draw:
                points.append(camera.world_to_screen(x, y))

            pygame.draw.lines(screen, (180, 180, 180), False, points, 2)

        
        # ---- POSICIÓN EN PANTALLA ----
        screen_pos = camera.world_to_screen(self.x, self.y)

        radius_pixels = self.radius * camera.pixels_per_meter * camera.zoom
        radius_pixels = max(int(radius_pixels), 1)

        pygame.draw.circle(screen, ANT_COLOR, screen_pos, radius_pixels)

        # ---- COMIDA QUE CARGA ----
        if self.state == "ReturningFood":

            food_offset = radius_pixels * 1.5

            food_x = screen_pos[0] + math.cos(self.angle) * food_offset
            food_y = screen_pos[1] + math.sin(self.angle) * food_offset

            food_radius = max(2, radius_pixels // 2)

            pygame.draw.circle(screen, (0, 220, 0), (int(food_x), int(food_y)), food_radius)
