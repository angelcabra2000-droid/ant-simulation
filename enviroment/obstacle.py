import pygame


class Obstacle:

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, screen, camera):

        # Convertir posición del mundo a pantalla
        screen_pos = camera.world_to_screen(self.x, self.y)

        width_pixels = self.width * camera.pixels_per_meter * camera.zoom
        height_pixels = self.height * camera.pixels_per_meter * camera.zoom

        rect = pygame.Rect(
            screen_pos[0] - width_pixels/2,
            screen_pos[1] - height_pixels/2,
            width_pixels,
            height_pixels
        )

        pygame.draw.rect(screen, (120, 120, 120), rect)