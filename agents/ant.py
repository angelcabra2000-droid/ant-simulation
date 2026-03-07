import random
import math
import pygame
from config.settings import ANT_COLOR
from collections import deque

from agents.ant_behavior import AntBehavior


class Ant:
    def __init__(self, ant_id, world):
        self.id = ant_id

        # ---- DATOS BIOLÓGICOS ----
        self.caste = random.choice(["Worker", "Soldier"])
        self.state = "Exploring"
        self.carrying_food = False
        self.age = 0
        self.lifespan = random.uniform(300, 600)
        self.energy = 100
        self.target = None

        # ---- PROPIEDADES FÍSICAS ----
        self.body_length = 0.025
        self.radius = 0.004
        self.speed = 0.08
        self.vision_radius = 0.5

        # ---- DIRECCIÓN ----
        self.angle = random.uniform(0, 2 * math.pi)
        self.turn_timer = 0
        self.turn_interval = random.uniform(0.5, 2)

        # Spawn cerca del nido
        self.x = random.uniform(-1, 1)
        self.y = random.uniform(-1, 1)

        self.world = world

        self.trail = deque(maxlen=20000)
        self.trail_timer = 0
        self.trail_interval = 1

    def update(self, dt, world):
        AntBehavior.update(self, dt, world)

    def draw(self, screen, camera, show_trail=True):

        if show_trail and len(self.trail) > 1:

            points = []
            trail_to_draw = list(self.trail)[-2000:]

            for x, y in trail_to_draw:
                screen_point = camera.world_to_screen(x, y)
                points.append(screen_point)

            pygame.draw.lines(screen, (180,180,180), False, points, 2)

        screen_pos = camera.world_to_screen(self.x, self.y)

        radius_pixels = self.radius * camera.pixels_per_meter * camera.zoom
        radius_pixels = max(int(radius_pixels), 1)

        pygame.draw.circle(screen, ANT_COLOR, screen_pos, radius_pixels)

        # ---- VISIÓN ----
        vision_pixels = self.vision_radius * camera.pixels_per_meter * camera.zoom

        pygame.draw.circle(
            screen,
            (0,255,0),
            screen_pos,
            int(vision_pixels),
            1
        )

        