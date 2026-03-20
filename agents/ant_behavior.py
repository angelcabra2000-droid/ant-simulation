import random
import math
from enviroment.object_type import ObjectType


class AntBehavior:

    @staticmethod
    def update(ant, dt, world):

        # -----------------------------
        # LIMPIAR TARGET SI DESAPARECE
        # -----------------------------
        if ant.target is not None:
            if ant.target not in ant.world.obstacles.obstacles:
                ant.target = None
                ant.state = "Exploring"
                ant.is_eating = False

        # ---- ENVEJECIMIENTO ----
        ant.age += dt
        ant.energy -= dt * 0.5

        obj = AntBehavior.detect_objects(ant)

        if obj and ant.target is None:
            AntBehavior.react_to_object(ant, obj)

        # ------------------------
        # COMPORTAMIENTO POR ESTADO
        # ------------------------

        # ---- EXPLORAR ----
        if ant.state == "Exploring":

            ant.turn_timer += dt

            if ant.turn_timer >= ant.turn_interval:
                ant.turn_timer = 0
                ant.turn_interval = random.uniform(0.5, 2)
                ant.angle += random.uniform(-math.pi/6, math.pi/6)

        # ---- IR A COMIDA ----
        elif ant.state == "GoingToFood":

            if ant.target is None:
                ant.state = "Exploring"
                return

            dx = ant.target.x - ant.x
            dy = ant.target.y - ant.y
            ant.angle = math.atan2(dy, dx)

            # SOLO SI NO HA TERMINADO DE COMER
            if not ant.carrying_food and AntBehavior.circle_rect_collision(ant, ant.target):

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

                    # 🔴 EMPUJÓN PARA DESPEGARSE
                    push = ant.radius * 2
                    ant.x += math.cos(ant.angle) * push
                    ant.y += math.sin(ant.angle) * push

                    ant.state = "ReturningFood"
                    ant.target = None

                return

        # ---- REGRESAR AL NIDO ----
        elif ant.state == "ReturningFood":

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

        # ---- ESPERAR EN EL NIDO ----
        elif ant.state == "WaitingInNest":

            ant.nest_timer += dt

            if ant.nest_timer >= ant.nest_wait_time:
                ant.state = "Exploring"

        # ---- ATACAR ----
        elif ant.state == "Attacking":

            if ant.target:

                dx = ant.target.x - ant.x
                dy = ant.target.y - ant.y
                ant.angle = math.atan2(dy, dx)

                if AntBehavior.circle_rect_collision(ant, ant.target):

                    angle_away = math.atan2(
                        ant.y - ant.target.y,
                        ant.x - ant.target.x
                    )

                    push = ant.radius * 4
                    ant.x += math.cos(angle_away) * push
                    ant.y += math.sin(angle_away) * push

                    ant.angle = angle_away + random.uniform(-0.5, 0.5)

                    if ant.target:
                        ant.target.health -= 10

                        if ant.target.health <= 0:
                            if ant.target in ant.world.obstacles.obstacles:
                                ant.world.obstacles.obstacles.remove(ant.target)
                                ant.target = None
                                ant.state = "Exploring"
                                return

        # -------------------
        # EVITAR OBSTÁCULOS
        # -------------------
        AntBehavior.avoid_obstacles(ant)

        # -------------------
        # MOVIMIENTO
        # -------------------
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

        # ---- TRAIL ----
        ant.trail_timer += dt

        if ant.trail_timer >= ant.trail_interval:
            ant.trail.append((ant.x, ant.y))
            ant.trail_timer = 0

        # -------------------
        # LÍMITES DEL MUNDO
        # -------------------
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

    @staticmethod
    def detect_objects(ant):

        closest = None
        min_dist = ant.vision_radius

        for obj in ant.world.obstacles.obstacles:

            # 🔴 ignorar comida si ya lleva
            if obj.type == ObjectType.FOOD and ant.carrying_food:
                continue

            if obj.type not in [ObjectType.FOOD, ObjectType.DANGER]:
                continue

            dx = obj.x - ant.x
            dy = obj.y - ant.y

            distance = math.sqrt(dx * dx + dy * dy)

            if distance > ant.vision_radius:
                continue

            angle_to_obj = math.atan2(dy, dx)
            angle_diff = abs((angle_to_obj - ant.angle + math.pi) % (2 * math.pi) - math.pi)

            if angle_diff > ant.fov / 2:
                continue

            if distance < min_dist:
                closest = obj
                min_dist = distance

        return closest

    @staticmethod
    def react_to_object(ant, obj):

        if obj.type == ObjectType.FOOD:
            ant.target = obj
            ant.state = "GoingToFood"

        elif obj.type == ObjectType.DANGER:
            ant.target = obj
            ant.state = "Attacking"

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