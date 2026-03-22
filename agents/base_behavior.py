import math
from enviroment.object_type import ObjectType


class BaseBehavior:

    @staticmethod
    def clean_target(ant):
        if ant.target is not None:
            if ant.target not in ant.world.obstacles.obstacles:
                ant.target = None
                ant.state = "Exploring"
                ant.is_eating = False

    @staticmethod
    def aging(ant, dt):
        ant.age += dt
        ant.energy -= dt * 0.5

    @staticmethod
    def circle_rect_collision(ant, rect):
        left = rect.x - rect.width / 2
        right = rect.x + rect.width / 2
        top = rect.y - rect.height / 2
        bottom = rect.y + rect.height / 2

        closest_x = max(left, min(ant.x, right))
        closest_y = max(top, min(ant.y, bottom))

        dx = ant.x - closest_x
        dy = ant.y - closest_y

        return dx * dx + dy * dy < ant.radius * ant.radius

    @staticmethod
    def avoid_obstacles(ant):
        import math

        look_ahead = ant.radius * 3

        future_x = ant.x + math.cos(ant.angle) * look_ahead
        future_y = ant.y + math.sin(ant.angle) * look_ahead

        for obj in ant.world.obstacles.obstacles:

            if obj.type != ObjectType.OBSTACLE:
                continue

            left = obj.x - obj.width / 2
            right = obj.x + obj.width / 2
            top = obj.y - obj.height / 2
            bottom = obj.y + obj.height / 2

            if left < future_x < right and top < future_y < bottom:

                dx = obj.x - ant.x
                dy = obj.y - ant.y

                tangent_x = -dy
                tangent_y = dx

                ant.angle = math.atan2(tangent_y, tangent_x)
                return True

        return False

    @staticmethod
    def move(ant, dt, world):

        if ant.state != "WaitingInNest":

            if ant.is_eating:
                speed = 0
            else:
                speed = ant.speed

                if ant.state == "ReturningFood":
                    speed *= 0.5

            ant.current_speed = speed

            dx = math.cos(ant.angle) * ant.current_speed * dt
            dy = math.sin(ant.angle) * ant.current_speed * dt

            ant.x += dx
            ant.y += dy

        # límites
        if ant.x < -world.half_width:
            ant.x = -world.half_width
            ant.angle = math.pi - ant.angle

        if ant.x > world.half_width:
            ant.x = world.half_width
            ant.angle = math.pi - ant.angle

        if ant.y < -world.half_height:
            ant.y = -world.half_height
            ant.angle = -ant.angle

        if ant.y > world.half_height:
            ant.y = world.half_height
            ant.angle = -ant.angle