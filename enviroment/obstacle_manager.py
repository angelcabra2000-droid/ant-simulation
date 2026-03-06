from enviroment.obstacle import Obstacle
from enviroment.object_type import ObjectType


class ObstacleManager:

    def __init__(self):
        self.obstacles = []

    def add_obstacle(self, x, y, width=0.4, height=0.4, obj_type=ObjectType.OBSTACLE):

        obstacle = Obstacle(x, y, width, height, obj_type)

        self.obstacles.append(obstacle)

    def draw(self, screen, camera):

        for obstacle in self.obstacles:
            obstacle.draw(screen, camera)
    
    def remove_obstacle_at(self, x, y):

        for obstacle in self.obstacles:

            if (obstacle.x - obstacle.width/2 <= x <= obstacle.x + obstacle.width/2 and
                obstacle.y - obstacle.height/2 <= y <= obstacle.y + obstacle.height/2):

                self.obstacles.remove(obstacle)
                return