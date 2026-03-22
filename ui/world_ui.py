import pygame


class WorldUI:

    def __init__(self, screen_width):
        self.screen_width = screen_width

        self.reset_button = pygame.Rect(20, 20, 100, 32)

        self.button_font = pygame.font.SysFont("arial", 18)
        self.time_font = pygame.font.SysFont("arial", 20)

        self.edit_font = pygame.font.SysFont("arial", 16)

    def handle_event(self, event, world, camera, grid, world_width, world_height):

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # Botón Reiniciar
            if self.reset_button.collidepoint(event.pos):

                new_world = type(world)(world_width, world_height)

                camera.world = new_world
                grid.world = new_world

                return new_world
        return world

    def draw(self, screen, world, input_handler):
        self.draw_time(screen, world)
        self.draw_reset_button(screen)
        self.draw_edit_mode(screen, input_handler)
        self.draw_trail_mode(screen, input_handler)

    def draw_time(self, screen, world):
        minutes = int(world.world_time // 60)
        seconds = int(world.world_time % 60)

        time_text = f"Tiempo: {minutes:02}:{seconds:02}"
        surface = self.time_font.render(time_text, True, (255, 255, 255))

        rect = surface.get_rect(topright=(self.screen_width - 20, 20))
        screen.blit(surface, rect)

    def draw_reset_button(self, screen):
        mouse_pos = pygame.mouse.get_pos()

        if self.reset_button.collidepoint(mouse_pos):
            color = (70, 170, 70)
        else:
            color = (40, 120, 40)

        pygame.draw.rect(screen, color, self.reset_button, border_radius=8)

        text_surface = self.button_font.render("Reiniciar", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.reset_button.center)

        screen.blit(text_surface, text_rect)

    def draw_edit_mode(self, screen, input_handler):

        if input_handler.place_obstacle_mode:

            text = "Puedes editar el mundo"
            surface = self.edit_font.render(text, True, (255, 255, 255))

            rect = surface.get_rect()
            rect.topleft = (20, 70)

            screen.blit(surface, rect)

    def draw_trail_mode(self, screen, input_handler):

        # 🔴 modo seleccionado vs 🟢 todos
        if input_handler.only_selected_trail:
            color = (255, 100, 100)  # rojo
            mode_text = "Selected"
        else:
            color = (100, 255, 100)  # verde
            mode_text = "All"

        text = f"Trails: {mode_text}"

        surface = self.edit_font.render(text, True, color)

        rect = surface.get_rect()
        rect.topleft = (20, 100)  # debajo del modo edición

        screen.blit(surface, rect)