from typing import Mapping


import pyglet
from pyglet import shapes
# step 1 - draw a world. - a big blank screen
window = pyglet.window.Window()

ant_colour = 255, 255, 255
background = 0, 0, 0
# draw a fliping circle for our ant witch dies later  - https://pyglet.readthedocs.io/en/latest/modules/shapes.html#pyglet.shapes.Circle
#    add the shape to a pyglet.graphics.Batch for drawing.
 
class Ant: 
    def __init__(self):
        self.location = [200, 200]
        self.speed = [2, 0]
    
    def draw(self, batch):
        return shapes.Circle(self.location[0], self.location[1], 1, color=ant_colour, batch=batch)

    def update(self):
        self.location[0] += self.speed[0]
        self.location[1] += self.speed[1]

ant_1 = Ant()

fps_display = pyglet.window.FPSDisplay(window=window)

@window.event
def on_draw():
    window.clear()
    batch = pyglet.graphics.Batch()
    ant_shape = ant_1.draw(batch)
    batch.draw()
    fps_display.draw()

def update(dt):
    ant_1.update()

pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()
