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

        # =========================================================
        # PRIORIDAD GLOBAL: PELIGRO (visible) > OBJETIVO ACTUAL > FEROMONAS > EXPLORACIÓN
        # =========================================================

        # --- 1. DETECCIÓN DE ENEMIGO (máxima prioridad, siempre activa) ---
        # Independiente de cualquier otro estado o detección
        if ant.state not in ("Attacking", "WaitingInNest", "ReturningNest"):
            enemy = SoldierBehavior.detect_enemy(ant)
            if enemy:
                ant.target = enemy
                ant.state = "Attacking"

        # =========================================================
        # ESTADOS
        # =========================================================

        if ant.state == "Exploring":
            SoldierBehavior._state_exploring(ant, dt)

        elif ant.state == "Attacking":
            SoldierBehavior._state_attacking(ant, dt)

        elif ant.state == "FollowingDangerTrail":
            SoldierBehavior._state_following_danger_trail(ant, dt)

        elif ant.state == "ReturningNest":
            BaseBehavior.return_to_nest(ant, dt)

        elif ant.state == "WaitingInNest":
            SoldierBehavior._state_waiting_in_nest(ant, dt)

        BaseBehavior.avoid_obstacles(ant)
        BaseBehavior.move(ant, dt, world)

    # =========================================================
    # ESTADOS INTERNOS
    # =========================================================

    @staticmethod
    def _state_exploring(ant, dt):
        """
        1. Si ve peligro → Attacking  (manejado arriba en update)
        2. Si huele peligro → FollowingDangerTrail
        3. Si ve comida → marcar con feromona FOOD ocasionalmente
        4. Si nada → movimiento semi-aleatorio
        """
        # 2. Oler peligro (feromonas DANGER)
        danger_steer_x, danger_steer_y = SoldierBehavior.detect_danger_pheromones(ant)
        if danger_steer_x != 0 or danger_steer_y != 0:
            ant.state = "FollowingDangerTrail"
            return

        # 3. Ver comida → marcar ocasionalmente
        food = WorkerBehavior.detect_food(ant)
        if food:
            ant.pheromone_timer += 0  # el timer se acumula abajo con dt
            # La marca se deja en el timer global al final
            ant._saw_food_this_frame = True
        else:
            ant._saw_food_this_frame = False

        # Dejar feromona FOOD si vio comida
        ant.pheromone_timer += 0  # acumular fuera
        if getattr(ant, "_saw_food_this_frame", False):
            # usa un timer separado para no interferir con el de Attacking
            ant._food_mark_timer = getattr(ant, "_food_mark_timer", 0) + 0
        
        # 4. Movimiento semi-aleatorio
        ant.turn_timer += 0  # se acumula en el bloque unificado abajo

    @staticmethod
    def _state_exploring(ant, dt):
        """
        1. Si ve peligro → Attacking  (manejado arriba en update)
        2. Si huele peligro → FollowingDangerTrail
        3. Si ve comida → dejar feromona FOOD ocasionalmente
        4. Si nada → movimiento semi-aleatorio
        """
        # 2. Oler peligro (feromonas DANGER en el entorno)
        danger_steer_x, danger_steer_y = SoldierBehavior.detect_danger_pheromones(ant)
        if danger_steer_x != 0 or danger_steer_y != 0:
            ant.state = "FollowingDangerTrail"
            return

        # 3. Ver comida → marcar
        food = WorkerBehavior.detect_food(ant)
        if food:
            ant.pheromone_timer += dt
            if ant.pheromone_timer >= ant.pheromone_interval:
                ant.world.pheromones.append(Pheromone(ant.x, ant.y, "FOOD"))
                ant.pheromone_timer = 0
        else:
            # 4. Movimiento semi-aleatorio
            ant.turn_timer += dt
            if ant.turn_timer >= 0.3:
                ant.turn_timer = 0
                ant.angle += random.uniform(-math.pi / 6, math.pi / 6)

    @staticmethod
    def _state_attacking(ant, dt):
        """
        1. Ir hacia el enemigo
        2. Siempre dejar feromona DANGER
        3. Si colisiona → hacer daño + retroceso
        4. Si enemigo muere → Exploring
        """
        if ant.target is None:
            ant.state = "Exploring"
            return

        dx = ant.target.x - ant.x
        dy = ant.target.y - ant.y
        ant.angle = math.atan2(dy, dx)

        # Siempre dejar feromona DANGER
        ant.pheromone_timer += dt
        if ant.pheromone_timer >= ant.pheromone_interval:
            ant.world.pheromones.append(Pheromone(ant.x, ant.y, "DANGER"))
            ant.pheromone_timer = 0

        if BaseBehavior.circle_rect_collision(ant, ant.target):

            # Retroceso
            angle_away = math.atan2(ant.y - ant.target.y, ant.x - ant.target.x)
            push = ant.radius * 4
            ant.x += math.cos(angle_away) * push
            ant.y += math.sin(angle_away) * push
            ant.angle = angle_away + random.uniform(-0.5, 0.5)

            # Daño
            ant.target.health -= 10

            if ant.target.health <= 0:
                if ant.target in ant.world.obstacles.obstacles:
                    ant.world.obstacles.obstacles.remove(ant.target)
                ant.target = None
                ant.state = "Exploring"

    @staticmethod
    def _state_following_danger_trail(ant, dt):
        """
        1. Seguir gradiente de feromonas DANGER
        2. Dejar feromona DANGER (reforzar camino)
        3. Si encuentra enemigo → Attacking  (manejado arriba en update)
        4. Si pierde rastro → Exploring
        """
        steer_x, steer_y = SoldierBehavior.detect_danger_pheromones(ant)

        if steer_x == 0 and steer_y == 0:
            # Perdió el rastro
            ant.state = "Exploring"
            return

        # Seguir el gradiente
        desired_angle = math.atan2(steer_y, steer_x)
        angle_diff = (desired_angle - ant.angle + math.pi) % (2 * math.pi) - math.pi
        turn_force = angle_diff * 2
        ant.angle += max(-ant.turn_speed * dt, min(ant.turn_speed * dt, turn_force))

        # Reforzar el camino con feromona DANGER
        ant.pheromone_timer += dt
        if ant.pheromone_timer >= ant.pheromone_interval:
            ant.world.pheromones.append(Pheromone(ant.x, ant.y, "DANGER"))
            ant.pheromone_timer = 0

    @staticmethod
    def _state_waiting_in_nest(ant, dt):
        """
        Recuperar energía. Después de cierto tiempo → Exploring.
        """
        ant.nest_timer += dt
        ant.energy = min(100, ant.energy + 10 * dt)

        if ant.nest_timer >= ant.nest_wait_time and ant.energy >= 100:
            ant.state = "Exploring"
            ant.nest_timer = 0

    # =========================================================
    # UTILIDADES DE PERCEPCIÓN (solo retornan datos, sin decisiones)
    # =========================================================

    @staticmethod
    def detect_enemy(ant):
        """Retorna el enemigo más cercano dentro del FOV, o None."""
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

    @staticmethod
    def detect_danger_pheromones(ant):
        """
        Retorna vector de steering hacia el gradiente de feromonas DANGER.
        Usado para FollowingDangerTrail.
        """
        steer_x = 0
        steer_y = 0

        for p in ant.world.pheromones:

            if p.type != "DANGER":
                continue

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

            steer_x += dir_x * weight
            steer_y += dir_y * weight

        magnitude = math.sqrt(steer_x ** 2 + steer_y ** 2)
        if magnitude > 0:
            steer_x /= magnitude
            steer_y /= magnitude

        return steer_x, steer_y