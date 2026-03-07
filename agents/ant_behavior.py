import random
import math


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

        # ---- ENVEJECIMIENTO ----
        ant.age += dt
        ant.energy -= dt * 0.5

        obj = AntBehavior.detect_objects(ant)

        if ant.state == "Exploring" and obj:
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

            if ant.target:

                dx = ant.target.x - ant.x
                dy = ant.target.y - ant.y

                ant.angle = math.atan2(dy, dx)

                if AntBehavior.circle_rect_collision(ant, ant.target):

                    ant.carrying_food = True
                    ant.state = "ReturningFood"
                    ant.target = None

        # ---- VOLVER AL NIDO ----
        elif ant.state == "ReturningFood":

            dx = -ant.x
            dy = -ant.y

            ant.angle = math.atan2(dy, dx)

            dist = math.sqrt(ant.x*ant.x + ant.y*ant.y)

            if dist < 0.2:
                ant.state = "Exploring"
                ant.carrying_food = False

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

        # -------------------
        # MOVIMIENTO
        # -------------------

        dx = math.cos(ant.angle) * ant.speed * dt
        dy = math.sin(ant.angle) * ant.speed * dt

        ant.x += dx
        ant.y += dy

        # -------------------
        # COLISIONES CON OBSTÁCULOS
        # -------------------

        for obj in ant.world.obstacles.obstacles:

            if obj.type.name == "OBSTACLE":

                if AntBehavior.circle_rect_collision(ant, obj):

                    # vector hacia el obstáculo
                    dx = obj.x - ant.x
                    dy = obj.y - ant.y

                    # dirección tangencial (rodear)
                    tangent_x = -dy
                    tangent_y = dx

                    angle = math.atan2(tangent_y, tangent_x)

                    # pequeño empujón para no quedarse pegada
                    push = ant.radius * 0.5
                    ant.x -= dx * push
                    ant.y -= dy * push

                    # girar siguiendo el borde
                    ant.angle = angle + random.uniform(-0.2, 0.2)

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

    # ---------------------------------
    # DETECTAR OBJETOS
    # ---------------------------------

    @staticmethod
    def detect_objects(ant):

        closest = None
        min_dist = ant.vision_radius

        for obj in ant.world.obstacles.obstacles:

            dx = obj.x - ant.x
            dy = obj.y - ant.y

            distance = math.sqrt(dx*dx + dy*dy)

            if distance < min_dist:
                closest = obj
                min_dist = distance

        return closest

    # ---------------------------------
    # REACCIONAR A OBJETOS
    # ---------------------------------

    @staticmethod
    def react_to_object(ant, obj):

        # ---- COMIDA ----
        if obj.type.name == "FOOD":

            ant.target = obj
            ant.state = "GoingToFood"

        # ---- PELIGRO ----
        elif obj.type.name == "DANGER":

            ant.target = obj
            ant.state = "Attacking"

    # ---------------------------------
    # COLISIÓN CÍRCULO - RECTÁNGULO
    # ---------------------------------

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

        return dx*dx + dy*dy < ant.radius * ant.radius