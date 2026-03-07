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

        # ---- ENVEJECIMIENTO ----
        self.age += dt
        self.energy -= dt * 0.5

        obj = self.detect_objects()

        # SOLO detectar si explora
        if self.state == "Exploring" and obj:
            self.react_to_object(obj)

        # ------------------------
        # COMPORTAMIENTO POR ESTADO
        # ------------------------

        if self.state == "Exploring":

            self.turn_timer += dt

            if self.turn_timer >= self.turn_interval:
                self.turn_timer = 0
                self.turn_interval = random.uniform(0.5, 2)
                self.angle += random.uniform(-math.pi/6, math.pi/6)

        elif self.state == "ReturningFood":

            # ir al nido (0,0)
            dx = -self.x
            dy = -self.y
            self.angle = math.atan2(dy, dx)

            # si llega al nido vuelve a explorar
            if math.sqrt(self.x*self.x + self.y*self.y) < 0.2:
                self.state = "Exploring"

        elif self.state == "Attacking":

            if self.target:

                dx = self.target.x - self.x
                dy = self.target.y - self.y

                dist = math.sqrt(dx*dx + dy*dy)

                self.angle = math.atan2(dy, dx)

                # distancia mínima de ataque
                if dist < 0.1:
                    self.state = "Exploring"
                    self.target = None

        # -------------------
        # MOVIMIENTO
        # -------------------

        dx = math.cos(self.angle) * self.speed * dt
        dy = math.sin(self.angle) * self.speed * dt

        self.x += dx
        self.y += dy

        # ---- TRAIL ----
        self.trail_timer += dt

        if self.trail_timer >= self.trail_interval:
            self.trail.append((self.x, self.y))
            self.trail_timer = 0

        # ---- LÍMITES DEL MUNDO ----
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

    def detect_objects(self):

        closest = None
        min_dist = self.vision_radius

        for obj in self.world.obstacles.obstacles:

            dx = obj.x - self.x
            dy = obj.y - self.y

            distance = math.sqrt(dx*dx + dy*dy)

            if distance < min_dist:
                closest = obj
                min_dist = distance

        return closest


    def react_to_object(self, obj):

        if obj.type.name == "FOOD":

            self.state = "ReturningFood"

            dx = -self.x
            dy = -self.y
            self.angle = math.atan2(dy, dx)

        elif obj.type.name == "OBSTACLE":

            # calcular dirección hacia objeto
            dx = obj.x - self.x
            dy = obj.y - self.y

            angle_to_obj = math.atan2(dy, dx)

            # girar 90° para rodearlo
            self.angle = angle_to_obj + math.pi/2

        elif obj.type.name == "DANGER":

            self.state = "Attacking"
            self.target = obj

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