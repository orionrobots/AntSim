import random
from collections import namedtuple
import pyglet
from pyglet import shapes
# step 1 - draw a world. - a big blank screen
window = pyglet.window.Window()

Point = namedtuple("Point", ["x", "y"])

ant_colour = 0, 0, 0
background_colour = 43, 189, 98
border_colour = 255, 255, 0
nest_colour = 0xA0, 0x52, 0x2D

# draw a flipping circle for our ant witch dies later  - https://pyglet.readthedocs.io/en/latest/modules/shapes.html#pyglet.shapes.Circle
#    add the shape to a pyglet.graphics.Batch for drawing.
class Border:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = window.width - 1
        self.height = window.height - 1
    
    def draw(self, batch):
        return shapes.BorderedRectangle(self.x, self.y, self.width, self.height, 
            color=background_colour, 
            border_color=border_colour, batch=batch)

    def collide(self, location):
        return (location.x < self.x + 1) or (location.y < self.y + 1) \
            or (location.x > self.width -1 ) or (location.y > self.height - 1)
   

class Ant: 
    def __init__(self, location: Point):
        self.location = location
        self.speed = Point(0, 0)

    def draw(self, batch):
        return shapes.Circle(self.location.x, self.location.y, 1, color=ant_colour, batch=batch)

    def update(self):
        CHANCE_OF_ANT_DIR_CHANGE = 10 # 1 in 10
        if random.randint(0, CHANCE_OF_ANT_DIR_CHANGE) == 0:
            self.speed = Point(random.randint(-2, 2), random.randint(-2, 2))
        self.location = Point(self.location.x + self.speed.x, self.location.y + self.speed.y)

    def collision(self):
        self.speed = Point(-self.speed.x, -self.speed.y)
        self.update()
        self.update()


class Nest:
    def __init__(self, location: Point, size=20, population_limit=255) -> None:
        self.location = location
        self.size = size
        self.ants = []
        self.population_limit = population_limit

    def spawn_ant(self):
        self.ants.append(Ant(self.location))

    def draw(self, batch: pyglet.graphics.Batch):
        s_l = []
        s_l.append(shapes.Circle(self.location.x, self.location.y, self.size, color=nest_colour, batch=batch))
        s_l += [ant.draw(batch) for ant in self.ants]
        return s_l

    def update(self):
        CHANCE_OF_ANT_SPAWN = 3
        if len(self.ants) < self.population_limit and random.randint(0, CHANCE_OF_ANT_SPAWN) == 0:
            self.spawn_ant()


nest = Nest(Point(200, 200), population_limit=255)
border = Border()
fps_display = pyglet.window.FPSDisplay(window=window)

@window.event
def on_draw():
    window.clear()
    
    batch = pyglet.graphics.Batch()
    
    border_shapes = border.draw(batch)
    nest_shapes = nest.draw(batch)

    batch.draw()
    fps_display.draw()

def update(dt):
    nest.update()
    for ant in nest.ants:
        ant.update()
        if border.collide(ant.location):
            ant.collision()


pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()
