import pygame
import math
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

        cx = screen_pos[0]
        cy = screen_pos[1]

        # OBSTACULO → RECTANGULO MADERA
        if self.type == ObjectType.OBSTACLE:

            color = (139, 94, 60)  # café madera

            rect = pygame.Rect(
                cx - width_pixels/2,
                cy - height_pixels/2,
                width_pixels,
                height_pixels
            )

            pygame.draw.rect(screen, color, rect)


        # COMIDA → ROMBO
        elif self.type == ObjectType.FOOD:

            color = (34, 139, 34)  # verde hoja

            points = [
                (cx, cy - height_pixels/2),  # arriba
                (cx + width_pixels/2, cy),   # derecha
                (cx, cy + height_pixels/2),  # abajo
                (cx - width_pixels/2, cy)    # izquierda
            ]

            pygame.draw.polygon(screen, color, points)


        # PELIGRO → HEXAGONO
        elif self.type == ObjectType.DANGER:

            color = (200, 30, 30)

            radius = width_pixels / 2
            points = []

            for i in range(6):
                angle = math.radians(60 * i)
                px = cx + radius * math.cos(angle)
                py = cy + radius * math.sin(angle)
                points.append((px, py))

            pygame.draw.polygon(screen, color, points)