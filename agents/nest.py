# agents/nest.py

import pygame

class Nest:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.radius = 0.4  # metros

    def draw(self, screen, camera):
        screen_pos = camera.world_to_screen(self.x, self.y)
        radius_pixels = int(self.radius * camera.pixels_per_meter * camera.zoom)

        pygame.draw.circle(screen, (120, 70, 20), screen_pos, radius_pixels)