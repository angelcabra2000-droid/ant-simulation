import math
import random
from enviroment.object_type import ObjectType
from .base_behavior import BaseBehavior


class WorkerBehavior:

    @staticmethod
    def update(ant, dt, world):

        # -----------------------------
        # BASE
        # -----------------------------
        BaseBehavior.clean_target(ant)
        BaseBehavior.aging(ant, dt)

        # -----------------------------
        # DETECCIÓN
        # -----------------------------
        obj = WorkerBehavior.detect_food(ant)

        if obj and ant.target is None:
            ant.target = obj
            ant.state = "GoingToFood"

        # -----------------------------
        # ESTADOS
        # -----------------------------

        # ---- EXPLORAR ----
        if ant.state == "Exploring":

            ant.turn_timer += dt

            if ant.turn_timer >= ant.turn_interval:
                ant.turn_timer = 0
                ant.turn_interval = random.uniform(0.5, 2)
                ant.angle += random.uniform(-math.pi/6, math.pi/6)

        # ---- IR A COMIDA ----
        elif ant.state == "GoingToFood":
            WorkerBehavior.go_to_food(ant, dt)

        # ---- REGRESAR ----
        elif ant.state == "ReturningFood":
            WorkerBehavior.return_home(ant, dt)

        # ---- ESPERAR ----
        elif ant.state == "WaitingInNest":

            ant.nest_timer += dt

            if ant.nest_timer >= ant.nest_wait_time:
                ant.state = "Exploring"

        # -----------------------------
        # BASE FINAL
        # -----------------------------
        BaseBehavior.avoid_obstacles(ant)
        BaseBehavior.move(ant, dt, world)

    # =========================================================
    # 🔍 DETECCIÓN
    # =========================================================

    @staticmethod
    def detect_food(ant):

        closest = None
        min_dist = ant.vision_radius

        for obj in ant.world.obstacles.obstacles:

            if obj.type != ObjectType.FOOD:
                continue

            if ant.carrying_food:
                continue

            dx = obj.x - ant.x
            dy = obj.y - ant.y

            distance = math.sqrt(dx * dx + dy * dy)

            if distance == 0:
                continue

            if distance > ant.vision_radius:
                continue

            # -----------------------------
            # 👁️ FOV CON DOT PRODUCT
            # -----------------------------

            dir_x = dx / distance
            dir_y = dy / distance

            forward_x = math.cos(ant.angle)
            forward_y = math.sin(ant.angle)

            dot = dir_x * forward_x + dir_y * forward_y

            max_angle = math.cos(ant.fov / 2)

            if dot < max_angle:
                continue

            # -----------------------------

            if distance < min_dist:
                closest = obj
                min_dist = distance

        return closest
    
    
    @staticmethod
    def go_to_food(ant, dt):

        if ant.target is None:
            ant.state = "Exploring"
            return

        dx = ant.target.x - ant.x
        dy = ant.target.y - ant.y
        ant.angle = math.atan2(dy, dx)

        # ---- COMER ----
        if not ant.carrying_food and BaseBehavior.circle_rect_collision(ant, ant.target):

            if not ant.is_eating:
                ant.is_eating = True
                ant.eating_timer = ant.eating_time

            ant.current_speed = 0
            ant.eating_timer -= dt

            if ant.eating_timer <= 0:

                ant.is_eating = False
                ant.carrying_food = True

                if ant.target:
                    ant.target.health -= 20

                    if ant.target.health <= 0:
                        if ant.target in ant.world.obstacles.obstacles:
                            ant.world.obstacles.obstacles.remove(ant.target)

                # 🔴 EMPUJÓN (igual que antes)
                push = ant.radius * 2
                ant.x += math.cos(ant.angle) * push
                ant.y += math.sin(ant.angle) * push

                ant.state = "ReturningFood"
                ant.target = None

            return

    # =========================================================
    # 🏠 REGRESAR AL NIDO (TU LÓGICA ORIGINAL)
    # =========================================================

    @staticmethod
    def return_home(ant, dt):

        dx = -ant.x
        dy = -ant.y

        desired_angle = math.atan2(dy, dx)

        angle_diff = (desired_angle - ant.angle + math.pi) % (2 * math.pi) - math.pi
        ant.angle += max(-ant.turn_speed * dt, min(ant.turn_speed * dt, angle_diff))

        ant.return_turn_timer += dt

        if ant.return_turn_timer >= ant.return_turn_interval:
            ant.return_turn_timer = 0
            ant.return_turn_interval = random.uniform(0.2, 0.6)
            ant.angle += random.uniform(-0.4, 0.4)

        dist = math.sqrt(ant.x * ant.x + ant.y * ant.y)

        if dist < ant.world.nest.radius:
            ant.state = "WaitingInNest"
            ant.carrying_food = False
            ant.nest_timer = 0