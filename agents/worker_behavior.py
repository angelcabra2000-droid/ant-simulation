import math
import random
from enviroment.object_type import ObjectType
from .base_behavior import BaseBehavior
from enviroment.pheromone import Pheromone


class WorkerBehavior:

    @staticmethod
    def update(ant, dt, world):

        BaseBehavior.clean_target(ant)
        BaseBehavior.aging(ant, dt)
        BaseBehavior.check_energy(ant)

        # -----------------------------
        # 👁️ FEROMONAS
        # -----------------------------
        if ant.state == "Exploring":
            steer_x, steer_y = WorkerBehavior.detect_pheromones(ant)

            if steer_x != 0 or steer_y != 0:
                desired_angle = math.atan2(steer_y, steer_x)
                angle_diff = (desired_angle - ant.angle + math.pi) % (2 * math.pi) - math.pi

                turn_force = angle_diff * 2
                ant.angle += max(-ant.turn_speed * dt, min(ant.turn_speed * dt, turn_force))

        # -----------------------------
        # DETECCIÓN COMIDA
        # -----------------------------
        obj = WorkerBehavior.detect_food(ant)

        if obj and ant.target is None:
            ant.target = obj
            ant.state = "GoingToFood"

        # -----------------------------
        # ESTADOS
        # -----------------------------

        if ant.state == "Exploring":
            ant.turn_timer += dt

            if ant.turn_timer >= ant.turn_interval:
                ant.turn_timer = 0
                ant.turn_interval = random.uniform(0.5, 2)
                ant.angle += random.uniform(-math.pi/6, math.pi/6)

        elif ant.state == "GoingToFood":
            WorkerBehavior.go_to_food(ant, dt)

        elif ant.state == "ReturningFood":
            WorkerBehavior.return_home(ant, dt)

        elif ant.state == "ReturningNest":
            BaseBehavior.return_to_nest(ant, dt)

        elif ant.state == "WaitingInNest":
            ant.nest_timer += dt
            ant.energy = min(100, ant.energy + 10 * dt)

            if ant.nest_timer >= ant.nest_wait_time and ant.energy >= 100:
                ant.state = "Exploring"
                ant.nest_timer = 0

        BaseBehavior.avoid_obstacles(ant)
        BaseBehavior.move(ant, dt, world)

    # =========================================================
    # 🔍 DETECCIÓN COMIDA (CORREGIDO)
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

            if distance == 0 or distance > ant.vision_radius:
                continue

            dir_x = dx / distance
            dir_y = dy / distance

            forward_x = math.cos(ant.angle)
            forward_y = math.sin(ant.angle)

            dot = dir_x * forward_x + dir_y * forward_y
            max_angle = math.cos(ant.fov / 2)

            if dot < max_angle:
                continue

            if distance < min_dist:
                closest = obj
                min_dist = distance

        return closest

    # =========================================================
    # 🧪 FEROMONAS (MEJORADO)
    # =========================================================

    @staticmethod
    def detect_pheromones(ant):

        steer_x = 0
        steer_y = 0

        for p in ant.world.pheromones:

            dx = p.x - ant.x
            dy = p.y - ant.y

            dist = math.sqrt(dx * dx + dy * dy)

            if dist == 0 or dist > ant.vision_radius:
                continue

            # dirección normalizada
            dir_x = dx / dist
            dir_y = dy / dist

            # forward
            forward_x = math.cos(ant.angle)
            forward_y = math.sin(ant.angle)

            dot = dir_x * forward_x + dir_y * forward_y

            if dot < 0:
                continue

            direction_weight = dot ** 2

            falloff = 1 - (dist / ant.vision_radius)
            falloff = max(0, falloff)

            weight = p.strength * direction_weight * falloff

            if p.type == "DANGER":
                steer_x -= dir_x * weight
                steer_y -= dir_y * weight

            elif p.type == "FOOD" and not ant.carrying_food:
                steer_x += dir_x * weight
                steer_y += dir_y * weight

        # normalizar
        magnitude = math.sqrt(steer_x**2 + steer_y**2)

        if magnitude > 0:
            steer_x /= magnitude
            steer_y /= magnitude

        return steer_x, steer_y

    # =========================================================
    # 🍎 IR A COMIDA
    # =========================================================

    @staticmethod
    def go_to_food(ant, dt):

        if ant.target is None:
            ant.state = "Exploring"
            return

        dx = ant.target.x - ant.x
        dy = ant.target.y - ant.y
        ant.angle = math.atan2(dy, dx)

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

                push = ant.radius * 2
                ant.x += math.cos(ant.angle) * push
                ant.y += math.sin(ant.angle) * push

                ant.state = "ReturningFood"
                ant.target = None

    # =========================================================
    # 🏠 REGRESAR
    # =========================================================

    @staticmethod
    def return_home(ant, dt):

        dx = -ant.x
        dy = -ant.y

        desired_angle = math.atan2(dy, dx)

        angle_diff = (desired_angle - ant.angle + math.pi) % (2 * math.pi) - math.pi
        turn_force = angle_diff * 2
        ant.angle += max(-ant.turn_speed * dt, min(ant.turn_speed * dt, turn_force))

        # dejar feromona
        ant.pheromone_timer += dt
        if ant.pheromone_timer >= ant.pheromone_interval:
            ant.world.pheromones.append(
                Pheromone(ant.x, ant.y, "FOOD")
            )
            ant.pheromone_timer = 0

        dist = math.sqrt(ant.x * ant.x + ant.y * ant.y)

        if dist < ant.world.nest.radius:
            ant.state = "WaitingInNest"
            ant.carrying_food = False
            ant.nest_timer = 0