import pygame
import os
from config.settings import PANEL_COLOR, TEXT_COLOR


class AntInfoPanel:
    def __init__(self, width=250):
        self.width = width
        self.selected_ant = None
        self.visible = False

        self.font = pygame.font.SysFont(None, 24)

        image_path = os.path.join("ui", "assets", "ant.png")
        if os.path.exists(image_path):
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (150, 150))
        else:
            self.image = None

        self.close_button_rect = None

    def set_selected_agent(self, agent):
        self.selected_ant = agent
        self.visible = True

    def handle_event(self, event):
        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.close_button_rect and self.close_button_rect.collidepoint(event.pos):
                self.visible = False
                self.selected_ant = None

    def draw(self, screen):
        if not self.visible or not self.selected_ant:
            return

        screen_width = screen.get_width()
        screen_height = screen.get_height()

        panel_rect = pygame.Rect(
            screen_width - self.width, 0, self.width, screen_height
        )

        pygame.draw.rect(screen, PANEL_COLOR, panel_rect)

        # ----- BOTÓN CERRAR -----
        self.close_button_rect = pygame.Rect(
            screen_width - 30, 10, 20, 20
        )

        pygame.draw.rect(screen, (200, 50, 50), self.close_button_rect)

        close_text = self.font.render("X", True, (255, 255, 255))
        screen.blit(close_text, (screen_width - 25, 10))

        y_offset = 50

        if self.image:
            screen.blit(
                self.image,
                (screen_width - self.width + 50, 50)
            )
            y_offset += 170

        lines = [
            f"ID: {self.selected_ant.id}",
            f"State: {self.selected_ant.state}",
            f"Age: {self.selected_ant.age:.1f}s",
            f"Energy: {self.selected_ant.energy:.0f}",
            f"Pos: ({self.selected_ant.x:.2f}, {self.selected_ant.y:.2f}) m",
            f"Vel: {self.selected_ant.speed:.2f} m/s",
        ]

        for line in lines:
            text = self.font.render(line, True, TEXT_COLOR)
            screen.blit(text, (screen_width - self.width + 20, y_offset))
            y_offset += 30