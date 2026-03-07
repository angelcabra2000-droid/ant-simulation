import pygame
from enviroment.object_type import ObjectType


class Obstacle:

    def __init__(self, x, y, width, height, obj_type=ObjectType.OBSTACLE):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = obj_type

    @property
    def half_width(self):
        return self.width / 2

    @property
    def half_height(self):
        return self.height / 2

    def draw(self, screen, camera):

        screen_pos = camera.world_to_screen(self.x, self.y)

        width_pixels = self.width * camera.pixels_per_meter * camera.zoom
        height_pixels = self.height * camera.pixels_per_meter * camera.zoom

        rect = pygame.Rect(
            screen_pos[0] - width_pixels/2,
            screen_pos[1] - height_pixels/2,
            width_pixels,
            height_pixels
        )

        # Color según tipo
        if self.type.name == "OBSTACLE":
            color = (120,120,120)

        elif self.type.name == "FOOD":
            color = (0,200,0)

        elif self.type.name == "DANGER":
            color = (200,0,0)

        pygame.draw.rect(screen, color, rect)

    