import pygame
from config.settings import GRID_COLOR


class Grid:
    def __init__(self, world):
        self.world = world
        self.small_spacing = 0.1  # 10 cm
        self.big_spacing = 1.0    # 1 metro

    def draw(self, screen, camera):

        start_x = -self.world.half_width
        end_x = self.world.half_width

        start_y = -self.world.half_height
        end_y = self.world.half_height

        # -------- LINEAS FINAS (10 cm) --------
        x = start_x
        while x <= end_x:
            start = camera.world_to_screen(x, start_y)
            end = camera.world_to_screen(x, end_y)
            pygame.draw.line(screen, GRID_COLOR, start, end, 1)
            x += self.small_spacing

        y = start_y
        while y <= end_y:
            start = camera.world_to_screen(start_x, y)
            end = camera.world_to_screen(end_x, y)
            pygame.draw.line(screen, GRID_COLOR, start, end, 1)
            y += self.small_spacing

        # -------- LINEAS GRUESAS (1 metro) --------
        x = start_x
        while x <= end_x:
            start = camera.world_to_screen(x, start_y)
            end = camera.world_to_screen(x, end_y)
            pygame.draw.line(screen, GRID_COLOR, start, end, 2)
            x += self.big_spacing

        y = start_y
        while y <= end_y:
            start = camera.world_to_screen(start_x, y)
            end = camera.world_to_screen(end_x, y)
            pygame.draw.line(screen, GRID_COLOR, start, end, 2)
            y += self.big_spacing