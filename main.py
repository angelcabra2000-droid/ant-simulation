import pygame
import sys

from config.settings import *
from core.world import World
from core.camera import Camera
from core.grid import Grid
from core.input_handler import InputHandler
from ui.ant_info_panel import AntInfoPanel
from ui.world_ui import WorldUI
from ui.objectInfoPanel import ObjectInfoPanel


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Ant Simulation")

    clock = pygame.time.Clock()

    world = World(WORLD_WIDTH_METERS, WORLD_HEIGHT_METERS)
    world.load_state()

    camera = Camera(PIXELS_PER_METER, SCREEN_WIDTH, SCREEN_HEIGHT, world)
    grid = Grid(world)
    panel = AntInfoPanel()
    object_panel = ObjectInfoPanel()
    ui = WorldUI(SCREEN_WIDTH)
    input_handler = InputHandler()

    running = True

    while running:
        dt = clock.tick(FPS) / 1000

        # 🎮 Eventos
        running, world = input_handler.handle_events(
            pygame.event.get(),
            world,
            camera,
            grid,
            panel,
            object_panel,
            ui,
            WORLD_WIDTH_METERS,
            WORLD_HEIGHT_METERS
        )

        # 🎥 Movimiento cámara
        input_handler.handle_camera_movement(dt, camera, world)

        # 🌍 Actualizar mundo
        world.update(dt)

        # 🎨 Dibujar
        screen.fill(BACKGROUND_COLOR)

        if input_handler.show_grid:
            grid.draw(screen, camera)

        # =========================
        # 👻 PREVIEW DATA
        # =========================
        preview_data = None

        if input_handler.place_obstacle_mode:

            mouse_x, mouse_y = pygame.mouse.get_pos()

            world_x, world_y = camera.screen_to_world(
                mouse_x,
                mouse_y
            )

            width, height = input_handler.current_size.value

            preview_data = (
                world_x,
                world_y,
                width,
                height,
                input_handler.current_object_type
            )

        # =========================
        # 🌍 DRAW WORLD + PREVIEW
        # =========================
        world.draw(
            screen,
            camera,
            input_handler.show_trails,
            preview_data,
            panel,
            input_handler.only_selected_trail,
            input_handler.show_pheromones
        )

        ui.draw(screen, world, input_handler)

        panel.draw(screen)
        object_panel.draw(screen)
        

        pygame.display.flip()

    world.save_state()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()