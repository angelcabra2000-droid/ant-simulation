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

        # =========================================================
        # PRIORIDAD GLOBAL: PELIGRO > OBJETIVO ACTUAL > FEROMONAS > EXPLORACIÓN
        # =========================================================

        danger = WorkerBehavior.detect_danger(ant)

        if danger:
            if ant.state == "ReturningFood":
                pass  # el steering combinado ocurre dentro del estado
            elif ant.state not in ("AvoidingDanger", "WaitingInNest", "ReturningNest"):
                ant.target = None
                ant.is_eating = False
                ant.carrying_food = False
                ant.state = "AvoidingDanger"

        # =========================================================
        # ESTADOS
        # =========================================================

        if ant.state == "Exploring":
            WorkerBehavior._state_exploring(ant, dt)

        elif ant.state == "GoingToFood":
            WorkerBehavior._state_going_to_food(ant, dt)

        elif ant.state == "ReturningFood":
            WorkerBehavior._state_returning_food(ant, dt, danger)

        elif ant.state == "ReturningNest":
            BaseBehavior.return_to_nest(ant, dt)

        elif ant.state == "WaitingInNest":
            WorkerBehavior._state_waiting_in_nest(ant, dt)

        elif ant.state == "AvoidingDanger":
            WorkerBehavior._state_avoiding_danger(ant, dt)

        # FIX 3: evasión suave solo en ReturningFood, genérica para el resto
        if ant.state == "ReturningFood":
            WorkerBehavior._avoid_obstacles_soft(ant, dt)
        else:
            BaseBehavior.avoid_obstacles(ant)

        BaseBehavior.move(ant, dt, world)

    # =========================================================
    # ESTADOS INTERNOS
    # =========================================================

    @staticmethod
    def _state_exploring(ant, dt):
        food = WorkerBehavior.detect_food(ant)
        if food:
            ant.target = food
            ant.state = "GoingToFood"
            return

        steer_x, steer_y = WorkerBehavior.detect_pheromones(ant)

        if steer_x != 0 or steer_y != 0:
            desired_angle = math.atan2(steer_y, steer_x)
            angle_diff = (desired_angle - ant.angle + math.pi) % (2 * math.pi) - math.pi
            turn_force = angle_diff * 2
            ant.angle += max(-ant.turn_speed * dt, min(ant.turn_speed * dt, turn_force))
        else:
            ant.turn_timer += dt
            if ant.turn_timer >= ant.turn_interval:
                ant.turn_timer = 0
                ant.turn_interval = random.uniform(0.5, 2)
                ant.angle += random.uniform(-math.pi / 6, math.pi / 6)

    @staticmethod
    def _state_going_to_food(ant, dt):
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

    @staticmethod
    def _state_returning_food(ant, dt, danger=None):
        """
        1. Ir hacia el nido
        2. FIX 2: steering combinado con repulsión dinámica — cuanto más cerca el
           peligro, más domina la repulsión. A distancia cero es 100% repulsión,
           a vision_radius es 100% nido.
        3. Siempre dejar feromona FOOD
        4. Si llega al nido → WaitingInNest
        """
        # Vector normalizado hacia el nido
        nest_dx = -ant.x
        nest_dy = -ant.y
        nest_dist = math.sqrt(nest_dx * nest_dx + nest_dy * nest_dy)
        if nest_dist > 0:
            nest_dx /= nest_dist
            nest_dy /= nest_dist

        # FIX 2: pesos dinámicos según distancia al peligro
        if danger is not None:
            dx_d = ant.x - danger.x
            dy_d = ant.y - danger.y
            danger_dist = math.sqrt(dx_d * dx_d + dy_d * dy_d)

            if danger_dist > 0:
                # t=0 → peligro encima (repulsión domina)
                # t=1 → peligro en el borde del radio (nido domina)
                t = min(1.0, danger_dist / ant.vision_radius)

                # Peso nido crece con t, peso repulsión decrece con t
                # Mínimo del nido: 0.4 (siempre mantiene algo de dirección al nido)
                nest_weight      = 0.4 + 0.6 * t
                repulsion_weight = 1.0 - nest_weight

                repulse_x = (dx_d / danger_dist) * repulsion_weight
                repulse_y = (dy_d / danger_dist) * repulsion_weight

                combined_x = nest_dx * nest_weight + repulse_x
                combined_y = nest_dy * nest_weight + repulse_y
            else:
                combined_x = nest_dx
                combined_y = nest_dy
        else:
            combined_x = nest_dx
            combined_y = nest_dy

        # Normalizar y aplicar steering suave
        mag = math.sqrt(combined_x * combined_x + combined_y * combined_y)
        if mag > 0:
            combined_x /= mag
            combined_y /= mag

        desired_angle = math.atan2(combined_y, combined_x)
        angle_diff = (desired_angle - ant.angle + math.pi) % (2 * math.pi) - math.pi
        turn_force = angle_diff * 2
        ant.angle += max(-ant.turn_speed * dt, min(ant.turn_speed * dt, turn_force))

        # Siempre dejar feromona FOOD
        ant.pheromone_timer += dt
        if ant.pheromone_timer >= ant.pheromone_interval:
            ant.world.pheromones.append(Pheromone(ant.x, ant.y, "FOOD"))
            ant.pheromone_timer = 0

        # Llegó al nido
        dist = math.sqrt(ant.x * ant.x + ant.y * ant.y)
        if dist < ant.world.nest.radius:
            ant.carrying_food = False
            ant.energy = min(100, ant.energy + 20)
            ant.state = "WaitingInNest"
            ant.nest_timer = 0

    @staticmethod
    def _state_waiting_in_nest(ant, dt):
        ant.nest_timer += dt
        ant.energy = min(100, ant.energy + 10 * dt)
        if ant.nest_timer >= ant.nest_wait_time and ant.energy >= 100:
            ant.state = "Exploring"
            ant.nest_timer = 0

    @staticmethod
    def _state_avoiding_danger(ant, dt):
        danger = WorkerBehavior.detect_danger(ant)
        if danger is None:
            ant.state = "Exploring"
            return

        dx = ant.x - danger.x
        dy = ant.y - danger.y
        ant.angle = math.atan2(dy, dx)

        ant.pheromone_timer += dt
        if ant.pheromone_timer >= ant.pheromone_interval:
            ant.world.pheromones.append(Pheromone(ant.x, ant.y, "DANGER"))
            ant.pheromone_timer = 0

    # =========================================================
    # FIX 3: EVASIÓN SUAVE DE OBSTÁCULOS (solo ReturningFood)
    # =========================================================

    @staticmethod
    def _avoid_obstacles_soft(ant, dt):
        """
        El problema del original: look_ahead corto + giro instantáneo.
        La solución: look_ahead largo para detectar con anticipación suficiente
        para que el giro suave (con turn_speed) llegue a tiempo.

        Además elige el lado que menos desvía respecto al nido.
        """
        # look_ahead proporcional a la velocidad actual para anticipar correctamente
        # ant.speed * 0.5 porque ReturningFood va a mitad de velocidad
        effective_speed = ant.speed * 0.5
        # Cuántos segundos de anticipación queremos (suficiente para girar)
        # turn_speed ≈ 3 rad/s, necesitamos ~π/2 rad → ~0.5s de margen mínimo
        look_ahead = max(ant.radius * 8, effective_speed * 0.8)

        future_x = ant.x + math.cos(ant.angle) * look_ahead
        future_y = ant.y + math.sin(ant.angle) * look_ahead

        for obj in ant.world.obstacles.obstacles:

            if obj.type != ObjectType.OBSTACLE:
                continue

            # Expandir el bounding box por el radio de la hormiga para
            # detectar colisión real (no solo el punto futuro)
            half_w = obj.width  / 2 + ant.radius
            half_h = obj.height / 2 + ant.radius

            left   = obj.x - half_w
            right  = obj.x + half_w
            top    = obj.y - half_h
            bottom = obj.y + half_h

            if not (left < future_x < right and top < future_y < bottom):
                continue

            # Vector desde la hormiga al centro del obstáculo
            to_obj_x = obj.x - ant.x
            to_obj_y = obj.y - ant.y

            # Tangentes: rotar 90° en ambos sentidos
            angle_left  = math.atan2(-to_obj_x,  to_obj_y)
            angle_right = math.atan2( to_obj_x, -to_obj_y)

            # Ángulo ideal: dirección al nido
            nest_angle = math.atan2(-ant.y, -ant.x)

            # Elegir el lado que menos desvía del nido
            diff_left  = abs((angle_left  - nest_angle + math.pi) % (2 * math.pi) - math.pi)
            diff_right = abs((angle_right - nest_angle + math.pi) % (2 * math.pi) - math.pi)

            best_angle = angle_left if diff_left <= diff_right else angle_right

            # Steering suave con turn_speed
            angle_diff = (best_angle - ant.angle + math.pi) % (2 * math.pi) - math.pi
            turn_force = angle_diff * 3
            ant.angle += max(-ant.turn_speed * dt, min(ant.turn_speed * dt, turn_force))

            return  # un obstáculo a la vez

    # =========================================================
    # UTILIDADES DE PERCEPCIÓN
    # =========================================================

    @staticmethod
    def detect_food(ant):
        closest  = None
        min_dist = ant.vision_radius

        for obj in ant.world.obstacles.obstacles:
            if obj.type != ObjectType.FOOD or ant.carrying_food:
                continue

            dx = obj.x - ant.x
            dy = obj.y - ant.y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance == 0 or distance > ant.vision_radius:
                continue

            dir_x = dx / distance
            dir_y = dy / distance
            dot = dir_x * math.cos(ant.angle) + dir_y * math.sin(ant.angle)

            if dot < math.cos(ant.fov / 2):
                continue

            if distance < min_dist:
                closest  = obj
                min_dist = distance

        return closest

    @staticmethod
    def detect_danger(ant):
        closest  = None
        min_dist = ant.vision_radius

        for obj in ant.world.obstacles.obstacles:
            if obj.type != ObjectType.DANGER:
                continue

            dx = obj.x - ant.x
            dy = obj.y - ant.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < min_dist:
                closest  = obj
                min_dist = dist

        return closest

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

            dir_x = dx / dist
            dir_y = dy / dist
            dot = dir_x * math.cos(ant.angle) + dir_y * math.sin(ant.angle)

            if dot < 0:
                continue

            direction_weight = dot ** 2
            falloff = max(0, 1 - (dist / ant.vision_radius))
            weight  = p.strength * direction_weight * falloff

            if p.type == "DANGER":
                steer_x -= dir_x * weight
                steer_y -= dir_y * weight
            elif p.type == "FOOD" and not ant.carrying_food:
                steer_x += dir_x * weight
                steer_y += dir_y * weight

        magnitude = math.sqrt(steer_x ** 2 + steer_y ** 2)
        if magnitude > 0:
            steer_x /= magnitude
            steer_y /= magnitude

        return steer_x, steer_y