import pygame
from enviroment.object_type import ObjectType


class InputHandler:

    def __init__(self):
        self.show_grid = True
        self.show_trails = True
        self.place_obstacle_mode = False
        self.current_object_type = ObjectType.OBSTACLE

    def handle_events(self, events, world, camera, grid, panel, ui, world_width, world_height):

        for event in events:

            # ========================
            # SALIR
            # ========================
            if event.type == pygame.QUIT:
                world.save_state()
                return False, world

            # ========================
            # TECLAS
            # ========================
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_g:
                    self.show_grid = not self.show_grid

                if event.key == pygame.K_SPACE:
                    world.paused = not world.paused

                if event.key == pygame.K_t:
                    self.show_trails = not self.show_trails

                if event.key == pygame.K_o:
                    self.place_obstacle_mode = not self.place_obstacle_mode

                if event.key == pygame.K_1:
                    self.current_object_type = ObjectType.OBSTACLE

                if event.key == pygame.K_2:
                    self.current_object_type = ObjectType.FOOD

                if event.key == pygame.K_3:
                    self.current_object_type = ObjectType.DANGER

            # ========================
            # MOUSE
            # ========================
            if event.type == pygame.MOUSEBUTTONDOWN:

                mouse_pos = event.pos  # 🔥 siempre definir primero

                # Scroll zoom
                if event.button == 4:
                    camera.zoom_in()

                elif event.button == 5:
                    camera.zoom_out()

                # ========================
                # CLICK DERECHO (BORRAR OBSTÁCULO)
                # ========================
                elif event.button == 3:

                    world_x, world_y = camera.screen_to_world(
                        mouse_pos[0],
                        mouse_pos[1]
                    )

                    world.obstacles.remove_obstacle_at(world_x, world_y)

                    continue

                # ========================
                # CLICK IZQUIERDO
                # ========================
                elif event.button == 1:

                    # ========================
                    # CREAR OBSTÁCULO
                    # ========================
                    if self.place_obstacle_mode:

                        world_x, world_y = camera.screen_to_world(
                            mouse_pos[0],
                            mouse_pos[1]
                        )

                        world.obstacles.add_obstacle(
                            world_x,
                            world_y,
                            obj_type=self.current_object_type
                        )

                        continue

                    # ========================
                    # PANEL
                    # ========================
                    panel.handle_event(event)

                    # ========================
                    # SELECCIONAR HORMIGA
                    # ========================
                    for ant in world.ants:

                        ant_screen = camera.world_to_screen(ant.x, ant.y)

                        if pygame.math.Vector2(mouse_pos).distance_to(ant_screen) < 10:
                            panel.set_selected_agent(ant)
                            break

            # ========================
            # UI (reset)
            # ========================
            world = ui.handle_event(
                event,
                world,
                camera,
                grid,
                world_width,
                world_height
            )

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