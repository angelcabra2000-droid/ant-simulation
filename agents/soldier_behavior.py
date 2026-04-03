import math
import random
from enviroment.object_type import ObjectType
from .base_behavior import BaseBehavior
from enviroment.pheromone import Pheromone
from .worker_behavior import WorkerBehavior


class SoldierBehavior:

    @staticmethod
    def update(ant, dt, world):

        BaseBehavior.clean_target(ant)
        BaseBehavior.aging(ant, dt)
        BaseBehavior.check_energy(ant)

        # 🧪 marcar comida (sin ir)
        food = WorkerBehavior.detect_food(ant)
        if food:
            ant.pheromone_timer += dt
            if ant.pheromone_timer >= ant.pheromone_interval:
                ant.world.pheromones.append(
                    Pheromone(ant.x, ant.y, "FOOD")
                )
                ant.pheromone_timer = 0

        # -----------------------------
        # DETECCIÓN ENEMIGOS
        # -----------------------------
        obj = SoldierBehavior.detect_enemy(ant)

        if obj and ant.target is None and ant.state not in ("ReturningNest", "WaitingInNest"):
            ant.target = obj
            ant.state = "Attacking"

        # -----------------------------
        # ESTADOS
        # -----------------------------

        if ant.state == "Exploring":
            ant.turn_timer += dt

            if ant.turn_timer >= 0.3:
                ant.turn_timer = 0
                ant.angle += random.uniform(-math.pi/6, math.pi/6)

        elif ant.state == "Attacking":
            SoldierBehavior.attack(ant, dt)

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
    # 🔍 DETECCIÓN ENEMIGOS
    # =========================================================

    @staticmethod
    def detect_enemy(ant):

        closest = None
        min_dist = ant.vision_radius

        for obj in ant.world.obstacles.obstacles:

            if obj.type != ObjectType.DANGER:
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
    # ⚔️ ATAQUE + FEROMONA DE PELIGRO
    # =========================================================

    @staticmethod
    def attack(ant, dt):

        if ant.target:

            dx = ant.target.x - ant.x
            dy = ant.target.y - ant.y
            ant.angle = math.atan2(dy, dx)

            # 🧪 dejar feromona de peligro
            ant.pheromone_timer += dt
            if ant.pheromone_timer >= ant.pheromone_interval:
                ant.world.pheromones.append(
                    Pheromone(ant.x, ant.y, "DANGER")
                )
                ant.pheromone_timer = 0

            if BaseBehavior.circle_rect_collision(ant, ant.target):

                angle_away = math.atan2(
                    ant.y - ant.target.y,
                    ant.x - ant.target.x
                )

                push = ant.radius * 4
                ant.x += math.cos(angle_away) * push
                ant.y += math.sin(angle_away) * push

                ant.angle = angle_away + random.uniform(-0.5, 0.5)

                ant.target.health -= 10

                if ant.target.health <= 0:

                    if ant.target in ant.world.obstacles.obstacles:
                        ant.world.obstacles.obstacles.remove(ant.target)

                    ant.target = None
                    ant.state = "Exploring"