import random
import math
import pygame
from config.settings import ANT_COLOR
from collections import deque


class Ant:
    def __init__(self, ant_id, world):
        self.id = ant_id

        # ---- DATOS BIOLÓGICOS ----
        self.caste = random.choice(["Worker", "Soldier"])
        self.state = "Exploring"
        self.age = 0
        self.lifespan = random.uniform(300, 600)
        self.energy = 100

        # ---- PROPIEDADES FÍSICAS REALES ----
        self.body_length = 0.025  # 2.5 cm largo real
        self.radius = 0.004       # 4 mm aprox grosor
        self.speed = 0.3     # m/s realista

        # ---- DIRECCIÓN ----
        self.angle = random.uniform(0, 2 * math.pi)
        self.turn_timer = 0
        self.turn_interval = random.uniform(0.5, 2)

        # Spawn cerca del nido (0,0)
        self.x = random.uniform(-1, 1)
        self.y = random.uniform(-1, 1)

        self.world = world

        self.trail = deque(maxlen=20000)
        self.trail_timer = 0
        self.trail_interval = 0.5

    def update(self, dt, world):

        # Envejecer
        self.age += dt
        self.energy -= dt * 0.5

        # Cambio semi-aleatorio de dirección
        self.turn_timer += dt

        if self.turn_timer >= self.turn_interval:
            self.turn_timer = 0
            self.turn_interval = random.uniform(0.5, 2)
            self.angle += random.uniform(-math.pi/6, math.pi/6)

        dx = math.cos(self.angle) * self.speed * dt
        dy = math.sin(self.angle) * self.speed * dt

        self.x += dx
        self.y += dy

        self.trail_timer += dt

        if self.trail_timer >= self.trail_interval:
            self.trail.append((self.x, self.y))
            self.trail_timer = 0



        # Límites cartesianos (-50, 50)
        if self.x < -world.half_width:
            self.x = -world.half_width
            self.angle = math.pi - self.angle

        if self.x > world.half_width:
            self.x = world.half_width
            self.angle = math.pi - self.angle

        if self.y < -world.half_height:
            self.y = -world.half_height
            self.angle = -self.angle

        if self.y > world.half_height:
            self.y = world.half_height
            self.angle = -self.angle

    def draw(self, screen, camera, show_trail=True):

        if show_trail and len(self.trail) > 1:

            points = []

            trail_to_draw = list(self.trail)[-2000:]

            for x, y in trail_to_draw:
                screen_point = camera.world_to_screen(x, y)
                points.append(screen_point)

            pygame.draw.lines(screen, (180,180,180), False, points, 2)

        screen_pos = camera.world_to_screen(self.x, self.y)

        # Escalado físico real
        radius_pixels = self.radius * camera.pixels_per_meter * camera.zoom

        # Evitar que desaparezca completamente al alejar zoom
        radius_pixels = max(int(radius_pixels), 1)

        pygame.draw.circle(screen, ANT_COLOR, screen_pos, radius_pixels)