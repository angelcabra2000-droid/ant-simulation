import pygame


class Nest:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 0.1  # tamaño del nido en metros

    def draw(self, screen, camera):

        center = camera.world_to_screen(self.x, self.y)

        size_pixels = self.size * camera.pixels_per_meter * camera.zoom
        size_pixels = int(size_pixels)

        color = (255, 0, 0)

        # Línea horizontal
        pygame.draw.line(
            screen,
            color,
            (center[0] - size_pixels, center[1]),
            (center[0] + size_pixels, center[1]),
            2
        )

        # Línea vertical
        pygame.draw.line(
            screen,
            color,
            (center[0], center[1] - size_pixels),
            (center[0], center[1] + size_pixels),
            2
        )