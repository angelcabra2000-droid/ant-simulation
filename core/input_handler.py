import pygame
from enviroment.object_type import ObjectType
from enviroment.object_size import ObjectSize


class InputHandler:

    def __init__(self):

        # visualización
        self.show_grid = False
        self.show_trails = False

        # modo de creación de objetos
        self.place_obstacle_mode = False
        self.current_object_type = ObjectType.OBSTACLE
        self.current_size = ObjectSize.MEDIUM

    # ---------------------------------

    def handle_events(self, events, world, camera, grid, panel, ui, world_width, world_height):

        for event in events:

            # ----- cerrar programa -----
            if event.type == pygame.QUIT:
                world.save_state()
                return False, world

            # ----- teclado -----
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_g:
                    self.show_grid = not self.show_grid

                elif event.key == pygame.K_SPACE:
                    world.paused = not world.paused

                elif event.key == pygame.K_t:
                    self.show_trails = not self.show_trails

                elif event.key == pygame.K_o:
                    self.place_obstacle_mode = not self.place_obstacle_mode

                elif event.key == pygame.K_1:
                    self.current_object_type = ObjectType.OBSTACLE

                elif event.key == pygame.K_2:
                    self.current_object_type = ObjectType.FOOD

                elif event.key == pygame.K_3:
                    self.current_object_type = ObjectType.DANGER

                elif event.key == pygame.K_z:
                    self.current_size = ObjectSize.SMALL

                elif event.key == pygame.K_x:
                    self.current_size = ObjectSize.MEDIUM

                elif event.key == pygame.K_c:
                    self.current_size = ObjectSize.LARGE

            # ----- mouse -----
            elif event.type == pygame.MOUSEBUTTONDOWN:

                mouse_pos = event.pos

                # zoom
                if event.button == 4:
                    camera.zoom_in()
                    continue

                if event.button == 5:
                    camera.zoom_out()
                    continue

                world_x, world_y = camera.screen_to_world(
                    mouse_pos[0],
                    mouse_pos[1]
                )

                # borrar objeto
                if event.button == 3:
                    world.obstacles.remove_obstacle_at(world_x, world_y)
                    continue

                # click izquierdo
                if event.button == 1:

                    # crear objeto
                    if self.place_obstacle_mode:

                        width, height = self.current_size.value

                        world.obstacles.add_obstacle(
                            world_x,
                            world_y,
                            width=width,
                            height=height,
                            obj_type=self.current_object_type
                        )
                        continue

                    # panel
                    panel.handle_event(event)

                    # seleccionar hormiga
                    for ant in world.ants:

                        ant_screen = camera.world_to_screen(ant.x, ant.y)

                        if pygame.math.Vector2(mouse_pos).distance_to(ant_screen) < 10:
                            panel.set_selected_agent(ant)
                            break

            # ----- UI -----
            world = ui.handle_event(
                event,
                world,
                camera,
                grid,
                world_width,
                world_height
            )

        return True, world

    # ---------------------------------

    def handle_camera_movement(self, dt, camera, world):

        if world.paused:
            return

        keys = pygame.key.get_pressed()

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