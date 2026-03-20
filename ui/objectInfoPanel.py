import pygame
import os
from config.settings import PANEL_COLOR, TEXT_COLOR


class ObjectInfoPanel:

    def __init__(self, width=220):

        self.width = width
        self.padding = 15

        self.selected_object = None
        self.visible = False

        self.font = pygame.font.SysFont(None, 22)

        # imágenes por tipo
        self.images = {
            "FOOD": self.load_image("food.png"),
            "DANGER": self.load_image("danger.png"),
            "OBSTACLE": self.load_image("obstacle.png"),
        }

        self.close_button_rect = None

    # ---------------------

    def load_image(self, filename):

        path = os.path.join("ui", "assets", filename)

        if os.path.exists(path):
            img = pygame.image.load(path)
            return pygame.transform.scale(img, (100, 100))

        return None

    # ---------------------

    def set_selected_object(self, obj):
        self.selected_object = obj
        self.visible = True

    # ---------------------

    def handle_event(self, event):

        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:

            if self.close_button_rect and self.close_button_rect.collidepoint(event.pos):
                self.visible = False
                self.selected_object = None

    # ---------------------

    def draw(self, screen):

        if not self.visible or not self.selected_object:
            return

        obj = self.selected_object
        screen_width = screen.get_width()

        # 🔴 obtener tipo como string
        obj_type = obj.type.name

        # 🔴 obtener tamaño (puedes mejorar esto luego)
        size_text = f"{obj.width:.2f} x {obj.height:.2f}"

        lines = [
            f"Type: {obj_type}",
            f"Size: {size_text}",
            f"Health: {getattr(obj, 'health', 'N/A')}",
        ]

        # ----- imagen según tipo -----
        image = self.images.get(obj_type, None)

        line_height = 28
        image_height = 100 if image else 0

        panel_height = (
            self.padding * 2 +
            image_height +
            len(lines) * line_height +
            20
        )

        panel_rect = pygame.Rect(
            screen_width - self.width - 10,
            10,
            self.width,
            panel_height
        )

        pygame.draw.rect(screen, PANEL_COLOR, panel_rect, border_radius=6)

        # ----- botón cerrar -----
        self.close_button_rect = pygame.Rect(
            panel_rect.right - 25,
            panel_rect.top + 5,
            20,
            20
        )

        pygame.draw.rect(screen, (200, 60, 60), self.close_button_rect)

        close_text = self.font.render("X", True, (255, 255, 255))
        screen.blit(close_text, (self.close_button_rect.x + 5, self.close_button_rect.y))

        y_offset = panel_rect.top + self.padding + 10

        # ----- imagen -----
        if image:
            screen.blit(
                image,
                (panel_rect.centerx - 50, y_offset)
            )
            y_offset += image_height + 10

        # ----- texto -----
        for line in lines:

            text = self.font.render(line, True, TEXT_COLOR)

            screen.blit(
                text,
                (panel_rect.left + self.padding, y_offset)
            )

            y_offset += line_height