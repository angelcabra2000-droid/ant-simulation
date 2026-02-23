import pygame


class InputHandler:

    def __init__(self):
        self.show_grid = True

    def handle_events(self, events, world, camera, grid, panel, ui, world_width, world_height):

        for event in events:

            # Salir
            if event.type == pygame.QUIT:
                world.save_state()
                return False, world

            # ========================
            # TECLAS
            # ========================
            if event.type == pygame.KEYDOWN:

                # Mostrar / ocultar grid
                if event.key == pygame.K_g:
                    self.show_grid = not self.show_grid

                # 🔥 Pausar / Reanudar simulación
                if event.key == pygame.K_SPACE:
                    world.paused = not world.paused

            # ========================
            # UI (botón reset)
            # ========================
            world = ui.handle_event(
                event,
                world,
                camera,
                grid,
                world_width,
                world_height
            )

            # ========================
            # Panel lateral
            # ========================
            panel.handle_event(event)

            # ========================
            # Mouse
            # ========================
            if event.type == pygame.MOUSEBUTTONDOWN:

                # Zoom con scroll
                if event.button == 4:
                    camera.zoom_in()
                elif event.button == 5:
                    camera.zoom_out()

                # Click izquierdo → selección hormiga
                elif event.button == 1:

                    mouse_pos = pygame.mouse.get_pos()

                    for ant in world.ants:
                        ant_screen = camera.world_to_screen(ant.x, ant.y)

                        if pygame.math.Vector2(mouse_pos).distance_to(ant_screen) < 10:
                            panel.set_selected_agent(ant)
                            break

        return True, world

    def handle_camera_movement(self, dt, camera, world):

        # Si está en pausa, no mover cámara
        if world.paused:
            return

        keys = pygame.key.get_pressed()

        # Ajustar movimiento según zoom
        zoom_factor = 1 / camera.zoom
        move_amount = camera.move_speed * zoom_factor * dt

        if keys[pygame.K_a]:
            camera.move(-move_amount, 0)
        if keys[pygame.K_d]:
            camera.move(move_amount, 0)
        if keys[pygame.K_w]:
            camera.move(0, move_amount)
        if keys[pygame.K_s]:
            camera.move(0, -move_amount)