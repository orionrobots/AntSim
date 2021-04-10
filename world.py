import typing
import enum
import random
import math

class Location:
    __slots__ = ['x', 'y']

    x: int
    y: int
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def distance(first: Location, second: Location):
        l = (second.x - first.x) ** 2
        w = (second.y - first.y) ** 2
        return sqrt(l + w)
    
    def __add__(self, other):
        return Location(self.x + other.x, self.y + other.y)

    @staticmethod
    def random(width: int, height: int):
        return Location(random.randint(width), random.randint(height))

    def generate_filled_circle(self: Location, radius: int):
        # Yield line start + end vectors
        # https://en.wikipedia.org/wiki/Midpoint_circle_algorithm
        # x**2 + y**2 = r ** 2
        x = radius
        y = 0

        sq_x = x ** 2 - (2 * y) - 1
        while sq_x > 0 and x > y:
            x = math.sqrt(sq_x)
            yield self + Location(-x, y),  self + Location(x, y)
            yield self + Location(-x, -y), self + Location(x, -y)
            yield self + Location(-y, -x), self + Location(y, -x)
            yield self + Location(-y, x),  self + Location(y, x)

            sq_x = sq_x - (2 * y) - 1
            y += 1


class AntMode(enum.IntEnum):
    exploring = 1
    foraging = 2
    returning = 3

class Ant:
    food: int
    direction: int
    mode: AntMode
    position: Location

    def __init__(self, nest: Location):
        self.food = 100
        self.direction = random.randint(359)
        self.mode = AntMode.exploring
        self.location = nest



class Cell:
    pher_from_nest :int
    new_pher_from_nest: int
    pher_from_food: int
    new_pher_from_food: int
    food: int
    obstacle: bool



class World:
    width = 100
    height = 100
    max_food_width = 15 # radius

    cells: typing.List[Cell]
    nest: Location

    population_size = 100
    ants: typing.List[Ant]

    def __init__(self):
        self.cells = [Cell() for n in self.width * self.height]
        self.nest = Location.random(self.width, self.height)
        self.add_food_source()
        self.ants = [Ant(self.nest) for n in self.population_size]

    def add_food_source(self):
        food_source = Location.random(self.width, self.height)
        food_width = random.randint(self.max_food_width)
        for start, end in food_source.generate_filled_circle(food_width):
            for n in range(start.x, end.x):
                self.locate_cell(Location(n, start.y)).food = 100

    def locate_cell(self, l: Location):
        return self.cells[l.y * width + l.x]

    def in_bounds(self, l: Location):
        return self.width > l.x > 0 and self.height > l.y >0

    def generate_in_bounds_neighbours(self, l: Location):
        candidates = [
            l + Location(1, 0),
            l - Location(1, 0),
            l + Location(0, 1),
            l - Location(0, 1),
            l + Location(1, 1),
            l - Location(1, 1)
        ]
        # todo - exclude obstacles here.
        return [candidate for candidate in candidates if self.in_bounds(candidate)]

    def update_cell_pheromones(self, l: Location):
        cell = self.locate_cell(l)
        neighbours = self.generate_in_bounds_neighbours(l)
        if cell.pher_from_food > 9:
            top_up_possible = [
                neighbour for neighbour in neighbours if neighbour.pher_from_food < cell.pher_from_food
            ]
            for neighbour in top_up_possible:
                neighbour.pher_from_food += 1
            cell.pher_from_food -= len(top_up_possible)
        elif cell.pher_from_food > 0:
            cell.pher_from_food -= 1

        if cell.pher_from_nest > 9:
            top_up_possible = [
                neighbour for neighbour in neighbours if neighbour.pher_from_nest < cell.pher_from_nest
            ]
            for neighbour in top_up_possible:
                neighbour.pher_from_nest += 1
            cell.pher_from_nest -= len(top_up_possible)
        elif cell.pher_from_nest > 0:
            cell.pher_from_nest -= 1  

    def update(self):
        # update pheremones
        for y in height:
            for x in width:
                l = Location(x, y)
                self.update_cell_pheromones(l)

        # Update ants
        [ant.update() for ant in self.ants]


