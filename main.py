import pygame
import sys

from config.settings import *
from core.world import World
from core.camera import Camera
from core.grid import Grid
from core.input_handler import InputHandler
from ui.ant_info_panel import AntInfoPanel
from ui.world_ui import WorldUI


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
            ui,
            WORLD_WIDTH_METERS,
            WORLD_HEIGHT_METERS
        )

        # 🎥 Movimiento cámara
        input_handler.handle_camera_movement(dt, camera)

        # 🌍 Actualizar mundo
        world.update(dt)

        # 🎨 Dibujar
        screen.fill(BACKGROUND_COLOR)

        if input_handler.show_grid:
            grid.draw(screen, camera)

        world.draw(screen, camera)

        ui.draw(screen, world)

        panel.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()