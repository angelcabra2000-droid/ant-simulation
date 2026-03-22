import math
import random
from enviroment.object_type import ObjectType
from .base_behavior import BaseBehavior


class SoldierBehavior:

    @staticmethod
    def update(ant, dt, world):

        BaseBehavior.clean_target(ant)
        BaseBehavior.aging(ant, dt)

        obj = SoldierBehavior.detect_enemy(ant)

        if obj and ant.target is None:
            ant.target = obj
            ant.state = "Attacking"

        if ant.state == "Exploring":

            ant.turn_timer += dt

            if ant.turn_timer >= 0.3:
                ant.turn_timer = 0
                ant.angle += random.uniform(-math.pi/3, math.pi/3)

        elif ant.state == "Attacking":
            SoldierBehavior.attack(ant, dt)

        BaseBehavior.avoid_obstacles(ant)
        BaseBehavior.move(ant, dt, world)

    # -------------------------

    @staticmethod
    def detect_enemy(ant):
        for obj in ant.world.obstacles.obstacles:
            if obj.type == ObjectType.DANGER:
                return obj
        return None
    
    @staticmethod
    def attack(ant, dt):

        if ant.target:

            dx = ant.target.x - ant.x
            dy = ant.target.y - ant.y
            ant.angle = math.atan2(dy, dx)

            # colisión
            if BaseBehavior.circle_rect_collision(ant, ant.target):

                # empujar hacia atrás
                angle_away = math.atan2(
                    ant.y - ant.target.y,
                    ant.x - ant.target.x
                )

                push = ant.radius * 4
                ant.x += math.cos(angle_away) * push
                ant.y += math.sin(angle_away) * push

                ant.angle = angle_away + random.uniform(-0.5, 0.5)

                # daño
                ant.target.health -= 10

                if ant.target.health <= 0:

                    if ant.target in ant.world.obstacles.obstacles:
                        ant.world.obstacles.obstacles.remove(ant.target)

                    ant.target = None
                    ant.state = "Exploring"