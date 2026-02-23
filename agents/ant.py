import random
import math
import pygame
from config.settings import ANT_COLOR


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
        self.radius = 0.025  # 2.5 cm reales
        self.speed = 0.3     # m/s realista

        # ---- DIRECCIÓN ----
        self.angle = random.uniform(0, 2 * math.pi)
        self.turn_timer = 0
        self.turn_interval = random.uniform(0.5, 2)

        # Spawn cerca del nido (0,0)
        self.x = random.uniform(-1, 1)
        self.y = random.uniform(-1, 1)

        self.world = world

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

    def draw(self, screen, camera):

        screen_pos = camera.world_to_screen(self.x, self.y)

        radius_pixels = int(
            self.radius * camera.pixels_per_meter * camera.zoom
        )

        pygame.draw.circle(screen, ANT_COLOR, screen_pos, max(radius_pixels, 1))