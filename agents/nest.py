import pygame


class Nest:

    def __init__(self):
        self.x = 0
        self.y = 0

        # radio real del nido (metros)
        self.radius = 0.1

    def draw(self, screen, camera):

        center = camera.world_to_screen(self.x, self.y)

        radius_pixels = self.radius * camera.pixels_per_meter * camera.zoom
        radius_pixels = int(radius_pixels)

        color = (255, 0, 0)

        # cruz interna (solo visual)
        pygame.draw.line(
            screen,
            color,
            (center[0] - radius_pixels, center[1]),
            (center[0] + radius_pixels, center[1]),
            2
        )

        pygame.draw.line(
            screen,
            color,
            (center[0], center[1] - radius_pixels),
            (center[0], center[1] + radius_pixels),
            2
        )