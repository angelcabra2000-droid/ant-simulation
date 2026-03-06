class Camera:
    def __init__(self, pixels_per_meter, screen_width, screen_height, world):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world = world
        self.pixels_per_meter = pixels_per_meter

        # Zoom mínimo para que el mundo completo quepa en pantalla
        zoom_x = screen_width / (world.half_width * 2 * pixels_per_meter)
        zoom_y = screen_height / (world.half_height * 2 * pixels_per_meter)

        self.min_zoom = min(zoom_x, zoom_y)
        self.max_zoom = self.min_zoom * 20

        self.zoom = self.min_zoom

        # Centro del mundo
        self.center_x = 0
        self.center_y = 0

        self.move_speed = 5  # metros por segundo

    def world_to_screen(self, x, y):
        screen_x = (x - self.center_x) * self.pixels_per_meter * self.zoom + self.screen_width / 2
        screen_y = -(y - self.center_y) * self.pixels_per_meter * self.zoom + self.screen_height / 2
        return int(screen_x), int(screen_y)
    
    def screen_to_world(self, screen_x, screen_y):

        world_x = (
            (screen_x - self.screen_width / 2) /
            (self.pixels_per_meter * self.zoom)
        ) + self.center_x

        world_y = (
            -(screen_y - self.screen_height / 2) /
            (self.pixels_per_meter * self.zoom)
        ) + self.center_y

        return world_x, world_y

    def move(self, dx, dy):
        self.center_x += dx
        self.center_y += dy
        self.clamp_position()

    def clamp_position(self):
        half_visible_width = (self.screen_width / 2) / (self.pixels_per_meter * self.zoom)
        half_visible_height = (self.screen_height / 2) / (self.pixels_per_meter * self.zoom)

        min_x = -self.world.half_width + half_visible_width
        max_x = self.world.half_width - half_visible_width

        min_y = -self.world.half_height + half_visible_height
        max_y = self.world.half_height - half_visible_height

        self.center_x = max(min_x, min(self.center_x, max_x))
        self.center_y = max(min_y, min(self.center_y, max_y))

    def zoom_in(self):
        self.zoom *= 1.1
        if self.zoom > self.max_zoom:
            self.zoom = self.max_zoom
        self.clamp_position()

    def zoom_out(self):
        self.zoom *= 0.9
        if self.zoom < self.min_zoom:
            self.zoom = self.min_zoom
        self.clamp_position()