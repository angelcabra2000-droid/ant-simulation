import pygame
import math


class Pheromone:

    def __init__(self, x, y, p_type, strength=1.0, life=120.0):

        self.x = x
        self.y = y

        self.type = p_type  # "food" o "danger"

        self.max_strength = strength
        self.life = life
        self.max_life = life

    # ---------------------------------

    @property
    def strength(self):
        if self.max_life == 0:
            return 0
        return self.max_strength * (self.life / self.max_life)
    

    def draw(self, screen, camera):

        screen_pos = camera.world_to_screen(self.x, self.y)

        life_ratio = max(0, self.life / self.max_life)

        # 🟢 COMIDA
        if self.type == "FOOD":
            color = (0, 255, 0)
            alpha = int(140 * life_ratio)
            radius = int(5 + 3 * life_ratio)

        # 🔴 PELIGRO
        else:
            color = (255, 50, 50)
            alpha = int(180 * life_ratio)
            radius = int(6 + 4 * life_ratio)

        # superficie con transparencia
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

        pygame.draw.circle(
            surf,
            (*color, alpha),
            (radius, radius),
            radius
        )

        screen.blit(surf, (screen_pos[0] - radius, screen_pos[1] - radius))