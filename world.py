import random
from collections import namedtuple
import sys

import pygame

pygame.init()
Point = namedtuple("Point", ["x", "y"])

screen = pygame.display.set_mode((800, 600))

ant_colour = 0, 0, 0
ant_with_food_colour = 255, 255, 255
background_colour = 43, 189, 98
border_colour = 255, 255, 0
nest_colour = 0xA0, 0x52, 0x2D
food_colour = 255, 255, 0
food_trail_colour = 255, 0, 255

# draw a flipping circle for our ant witch dies later  - https://pyglet.readthedocs.io/en/latest/modules/shapes.html#pyglet.shapes.Circle
#    add the shape to a pyglet.graphics.Batch for drawing.
class Border:
    def __init__(self, rect):
        self.rect = rect
    
    def draw(self, surface):
        surface.fill(background_colour, rect=self.rect)
        pygame.draw.rect(surface, border_colour, rect=self.rect, width=2)

    def collide(self, location):
        return not self.rect.collidepoint(*location)

def distance_sq(first_location: Point, second_location: Point) -> int:
    return (second_location.x - first_location.x) ** 2 + (second_location.y - first_location.y) ** 2


class PheremoneField:
    def __init__(self, colour) -> None:
        self.colour = colour

        self.add_size = 10
        self.saturation = 100
        self.field = {}

    def add_pheremone(self, location):
        self.field[location] = self.field.get(location, 0) + self.add_size
        if self.field[location] > self.saturation:
            self.field[location] = self.saturation

    def draw(self, surface: pygame.Surface):
        ph_surface = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        for location, strength in self.field.items():
            colour = pygame.Color(self.colour)
            colour.a = strength
            pygame.draw.rect(ph_surface, colour, pygame.Rect(location, (3, 3)))
        surface.blit(ph_surface, surface.get_rect())

    def update(self):
        for location in self.field.keys():
            self.field[location] -= 1
            if self.field[location] == 0:
                del self.field[location]


class Food:
    def __init__(self, location: Point, size=20):
        self.location = location
        self.size = size
        self.size_sq = size * size

    def draw(self, surface):
        pygame.draw.circle(surface, food_colour, self.location, self.size)

    def collide(self, location):
        return distance_sq(self.location, location) < self.size_sq


class Ant:
    def __init__(self, location: Point):
        self.location = location
        self.speed = Point(0, 0)
        self.found_food = False

    def draw(self, surface: pygame.Surface):
        if self.found_food:
            color = ant_with_food_colour
        else:
            color = ant_colour
        pygame.draw.rect(surface, color, pygame.Rect(self.location, (3, 3)))
        surface.set_at(self.location, color)

    def update(self):
        CHANCE_OF_ANT_DIR_CHANGE = 10 # 1 in 10
        if random.randint(0, CHANCE_OF_ANT_DIR_CHANGE) == 0:
            self.speed = Point(random.randint(-2, 2), random.randint(-2, 2))
        self.location = Point(self.location.x + self.speed.x, self.location.y + self.speed.y)

    def collision(self, other):
        if isinstance(other, Border):
            self.speed = Point(-self.speed.x, -self.speed.y)
            self.update()
            self.update()
        elif isinstance(other, Food):
            self.found_food = True


class Nest:
    def __init__(self, location: Point, size=20, population_limit=255) -> None:
        self.location = location
        self.size = size
        self.ants = []
        self.population_limit = population_limit

    def spawn_ant(self):
        self.ants.append(Ant(self.location))

    def draw(self, surface):
        pygame.draw.circle(surface, nest_colour, self.location, self.size)
        [ant.draw(surface) for ant in self.ants]

    def update(self):
        CHANCE_OF_ANT_SPAWN = 3
        if len(self.ants) < self.population_limit and random.randint(0, CHANCE_OF_ANT_SPAWN) == 0:
            self.spawn_ant()


nest = Nest(Point(200, 200), population_limit=255)
border = Border(screen.get_rect())
food = Food(Point(400, 100))
food_trail = PheremoneField(food_trail_colour)


def draw():
    screen.fill(background_colour)
       
    border.draw(screen)
    food.draw(screen)
    nest.draw(screen)
    food_trail.draw(screen)
    pygame.display.flip()


def update():
    nest.update()
    for ant in nest.ants:
        ant.update()
        if border.collide(ant.location):
            ant.collision(border)
        if food.collide(ant.location):
            ant.collision(food)
        if ant.found_food:
            food_trail.add_pheremone(ant.location)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            sys.exit()
    update()
    draw()
