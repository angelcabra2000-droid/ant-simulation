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

        # --- 1. DETECCIÓN DE PELIGRO (máxima prioridad, siempre activa) ---
        danger = WorkerBehavior.detect_danger(ant)

        if danger:
            # Si está en un estado donde el peligro modifica dirección (no cancela objetivo)
            if ant.state == "ReturningFood":
                # Solo hacer steering — mantener dirección general al nido
                WorkerBehavior._steer_away_from(ant, danger, dt)

            elif ant.state not in ("AvoidingDanger", "WaitingInNest", "ReturningNest"):
                # En cualquier otro estado activo: cambiar a AvoidingDanger
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
            WorkerBehavior._state_returning_food(ant, dt)

        elif ant.state == "ReturningNest":
            BaseBehavior.return_to_nest(ant, dt)

        elif ant.state == "WaitingInNest":
            WorkerBehavior._state_waiting_in_nest(ant, dt)

        elif ant.state == "AvoidingDanger":
            WorkerBehavior._state_avoiding_danger(ant, dt)

        BaseBehavior.avoid_obstacles(ant)
        BaseBehavior.move(ant, dt, world)

    # =========================================================
    # ESTADOS INTERNOS
    # =========================================================

    @staticmethod
    def _state_exploring(ant, dt):
        """
        1. Si ve comida → GoingToFood
        2. Si huele peligro → evitar + dejar feromona DANGER
        3. Si huele comida → seguir gradiente
        4. Si nada → movimiento semi-aleatorio
        """
        # 1. Ver comida (prioridad sobre feromonas)
        food = WorkerBehavior.detect_food(ant)
        if food:
            ant.target = food
            ant.state = "GoingToFood"
            return

        # 2 y 3. Feromonas (DANGER repele, FOOD atrae)
        steer_x, steer_y = WorkerBehavior.detect_pheromones(ant)

        if steer_x != 0 or steer_y != 0:
            desired_angle = math.atan2(steer_y, steer_x)
            angle_diff = (desired_angle - ant.angle + math.pi) % (2 * math.pi) - math.pi
            turn_force = angle_diff * 2
            ant.angle += max(-ant.turn_speed * dt, min(ant.turn_speed * dt, turn_force))
        else:
            # 4. Movimiento semi-aleatorio
            ant.turn_timer += dt
            if ant.turn_timer >= ant.turn_interval:
                ant.turn_timer = 0
                ant.turn_interval = random.uniform(0.5, 2)
                ant.angle += random.uniform(-math.pi / 6, math.pi / 6)

    @staticmethod
    def _state_going_to_food(ant, dt):
        """
        1. Si ve peligro → AvoidingDanger  (manejado arriba en update)
        2. Si llega a la comida → comer → ReturningFood
        3. Si pierde la comida → Exploring
        """
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
    def _state_returning_food(ant, dt):
        """
        1. Ir hacia el nido (vector directo)
        2. Si ve peligro → solo steering, mantener dirección general (manejado arriba)
        3. Siempre dejar feromona FOOD
        4. Si llega al nido → soltar comida → WaitingInNest
        """
        dx = -ant.x
        dy = -ant.y
        desired_angle = math.atan2(dy, dx)
        angle_diff = (desired_angle - ant.angle + math.pi) % (2 * math.pi) - math.pi
        turn_force = angle_diff * 2
        ant.angle += max(-ant.turn_speed * dt, min(ant.turn_speed * dt, turn_force))

        # Siempre dejar feromona FOOD
        ant.pheromone_timer += dt
        if ant.pheromone_timer >= ant.pheromone_interval:
            ant.world.pheromones.append(Pheromone(ant.x, ant.y, "FOOD"))
            ant.pheromone_timer = 0

        dist = math.sqrt(ant.x * ant.x + ant.y * ant.y)
        if dist < ant.world.nest.radius:
            ant.carrying_food = False
            ant.energy = min(100, ant.energy + 20)
            ant.state = "WaitingInNest"
            ant.nest_timer = 0

    @staticmethod
    def _state_waiting_in_nest(ant, dt):
        """
        1. Recuperar energía
        2. Después de cierto tiempo → Exploring
        """
        ant.nest_timer += dt
        ant.energy = min(100, ant.energy + 10 * dt)

        if ant.nest_timer >= ant.nest_wait_time and ant.energy >= 100:
            ant.state = "Exploring"
            ant.nest_timer = 0

    @staticmethod
    def _state_avoiding_danger(ant, dt):
        """
        1. Moverse en dirección opuesta al peligro
        2. Dejar feromona DANGER
        3. Cuando ya no detecta peligro → Exploring
        """
        danger = WorkerBehavior.detect_danger(ant)

        if danger is None:
            ant.state = "Exploring"
            return

        # Huir del peligro
        dx = ant.x - danger.x
        dy = ant.y - danger.y
        ant.angle = math.atan2(dy, dx)

        # Dejar feromona DANGER
        ant.pheromone_timer += dt
        if ant.pheromone_timer >= ant.pheromone_interval:
            ant.world.pheromones.append(Pheromone(ant.x, ant.y, "DANGER"))
            ant.pheromone_timer = 0

    # =========================================================
    # UTILIDADES DE PERCEPCIÓN (solo retornan datos, sin decisiones)
    # =========================================================

    @staticmethod
    def detect_food(ant):
        """Retorna el objeto de comida más cercano dentro del FOV, o None."""
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

    @staticmethod
    def detect_danger(ant):
        """Retorna el objeto de peligro más cercano dentro del radio de visión, o None."""
        closest = None
        min_dist = ant.vision_radius

        for obj in ant.world.obstacles.obstacles:

            if obj.type != ObjectType.DANGER:
                continue

            dx = obj.x - ant.x
            dy = obj.y - ant.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < min_dist:
                closest = obj
                min_dist = dist

        return closest

    @staticmethod
    def detect_pheromones(ant):
        """
        Retorna un vector de steering basado en feromonas visibles.
        FOOD: atrae (si no lleva comida)
        DANGER: repele (siempre)
        """
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

            forward_x = math.cos(ant.angle)
            forward_y = math.sin(ant.angle)

            dot = dir_x * forward_x + dir_y * forward_y

            if dot < 0:
                continue

            direction_weight = dot ** 2
            falloff = max(0, 1 - (dist / ant.vision_radius))
            weight = p.strength * direction_weight * falloff

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

    # =========================================================
    # HELPERS INTERNOS
    # =========================================================

    @staticmethod
    def _steer_away_from(ant, obj, dt):
        """Modifica el ángulo para evitar un objeto sin cambiar de estado."""
        dx = ant.x - obj.x
        dy = ant.y - obj.y
        avoid_angle = math.atan2(dy, dx)
        angle_diff = (avoid_angle - ant.angle + math.pi) % (2 * math.pi) - math.pi
        turn_force = angle_diff * 3
        ant.angle += max(-ant.turn_speed * dt, min(ant.turn_speed * dt, turn_force))