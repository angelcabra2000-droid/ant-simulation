import pygame
import os
from config.settings import PANEL_COLOR, TEXT_COLOR
from agents.ant_caste import AntCaste 


class AntInfoPanel:

    def __init__(self, width=220):

        self.width = width
        self.padding = 15

        self.selected_ant = None
        self.visible = False

        self.font = pygame.font.SysFont(None, 22)

        image_path = os.path.join("ui", "assets", "ant.png")

        if os.path.exists(image_path):
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (120, 120))
        else:
            self.image = None

        self.close_button_rect = None

    # ---------------------

    def set_selected_agent(self, agent):
        self.selected_ant = agent
        self.visible = True

    # ---------------------

    def handle_event(self, event):

        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:

            if self.close_button_rect and self.close_button_rect.collidepoint(event.pos):
                self.visible = False
                self.selected_ant = None

    # ---------------------

    def draw(self, screen):

        if not self.visible or not self.selected_ant:
            return

        screen_width = screen.get_width()

        lines = [
            f"ID: {self.selected_ant.id}",
            f"Caste: {self.selected_ant.caste.name}",
            f"State: {self.selected_ant.state}",
            f"Age: {self.selected_ant.age:.1f}s",
            f"Energy: {self.selected_ant.energy:.1f}%",  # ← nuevo
            f"Vel: {self.selected_ant.current_speed:.2f} m/s",
        ]

        # ----- calcular altura dinámica -----

        line_height = 28
        image_height = 120 if self.image else 0

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

        if self.image:

            screen.blit(
                self.image,
                (panel_rect.centerx - 60, y_offset)
            )

            y_offset += image_height + 10

        # ----- texto -----

        for line in lines:

            color = TEXT_COLOR

            if "Caste" in line:
                if self.selected_ant.caste == AntCaste.WORKER:
                    color = (100, 255, 100)
                elif self.selected_ant.caste == AntCaste.SOLDIER:
                    color = (255, 100, 100)

            elif "Energy" in line:
                energy = self.selected_ant.energy
                if energy > 60:
                    color = (100, 255, 100)   # verde
                elif energy > 20:
                    color = (255, 200, 50)    # amarillo
                else:
                    color = (255, 80, 80)     # rojo — peligro

            text = self.font.render(line, True, color)
            screen.blit(text, (panel_rect.left + self.padding, y_offset))
            y_offset += line_height