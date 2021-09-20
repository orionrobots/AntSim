import random
from collections import namedtuple
import sys

import pygame
from PIL import Image, ImageFilter

pygame.init()

screen = pygame.display.set_mode((800, 600))

ant_colour = pygame.Color(0, 0, 0)
ant_with_food_colour = pygame.Color(255, 255, 255)
background_colour = pygame.Color(43, 189, 98)
border_colour = pygame.Color(255, 255, 0)
nest_colour = pygame.Color(0xA0, 0x52, 0x2D)
food_colour = pygame.Color(255, 255, 0)
food_trail_colour = pygame.Color(255, 0, 255)
nest_trail_colour = pygame.Color(255, 128, 0)


class Border:
    def __init__(self, rect):
        self.rect = rect
    
    def draw(self, surface):
        surface.fill(background_colour, rect=self.rect)
        pygame.draw.rect(surface, border_colour, rect=self.rect, width=2)

    def collide(self, location):
        return not self.rect.collidepoint(*location)

def distance_sq(first_location: pygame.math.Vector2, second_location: pygame.math.Vector2) -> int:
    return (second_location.x - first_location.x) ** 2 + (second_location.y - first_location.y) ** 2


class PheremoneField:
    def __init__(self, colour, screen: pygame.Surface) -> None:
        self.colour = colour

        self.add_size = 10
        self.saturation = 255
        self.field = pygame.Surface(screen.get_size())
        self.update_field = pygame.Surface(screen.get_size())
        self.decay_surface = pygame.Surface(screen.get_size())
        decay_amount = 1
        self.decay_surface.fill((decay_amount, decay_amount, decay_amount))

    def add_pheremone(self, location, strength):
        hsla = self.colour.hsla 

        colour = pygame.Color(self.colour)
        colour.hsla = (hsla[0], hsla[1], int(hsla[2] * strength), hsla[3])

        self.update_field.set_at((int(location.x), int(location.y)), colour)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.field, surface.get_rect(), special_flags=pygame.BLEND_ADD)

    def update(self):
        self.field.blit(self.decay_surface, self.field.get_rect(), special_flags=pygame.BLEND_SUB)
        # Make it spread out a little
        image_mode = "RGBA"
        img = Image.frombytes(image_mode, self.field.get_size(), pygame.image.tostring(self.field, image_mode, False))
        blurred = img.filter(ImageFilter.GaussianBlur(radius=10))
        diffuse = pygame.image.fromstring(blurred.tobytes("raw", image_mode), self.field.get_size(), image_mode)
        diffuse.set_alpha(1)
        self.field.blit(diffuse, self.field.get_rect(), special_flags=pygame.BLEND_MAX)
        self.field.blit(self.update_field, self.field.get_rect(), special_flags=pygame.BLEND_MAX)
        self.update_field = pygame.Surface(screen.get_size())

    def sniff(self, location):
        if self.field.get_width() > location.x >= 0 and self.field.get_height() > location.y >= 0:
            location = (int(location.x), int(location.y))
            colour = self.field.get_at(location)
            return max(colour.r, colour.g, colour.b)
        else:
            return 0

class Food:
    def __init__(self, location: pygame.math.Vector2, size=20):
        self.location = location
        self.size = size
        self.size_sq = size * size

    def draw(self, surface):
        pygame.draw.circle(surface, food_colour, self.location, self.size)

    def collide(self, location):
        return self.location.distance_squared_to(location) < self.size_sq


class Ant:
    def __init__(self, location: pygame.math.Vector2, nest):
        self.location = location
        self.speed = pygame.math.Vector2(2, 0)
        self.found_food = False
        self.food_strength = 0
        self.nest_strength = 100
        self.nest = nest

    def draw(self, surface: pygame.Surface):
        if self.found_food:
            color = ant_with_food_colour
        else:
            color = ant_colour
        pygame.draw.rect(surface, color, pygame.Rect(self.location, (3, 3)))

    def sniff_in_dir(self, angle, trail):
        sn_dir = self.speed.rotate(angle)
        sniff_location = self.location + sn_dir
        scent = trail.sniff(sniff_location)
        return sn_dir, scent

    def update(self, food_trail: PheremoneField, nest_trail: PheremoneField):
        # What are we looking for?
        if self.found_food:
            sniffing_trail = nest_trail
        else:
            sniffing_trail = food_trail
        # Can we find a stronger smell?
        current_strength = sniffing_trail.sniff(self.location + self.speed)
        found_trail = False
        for angle in (-45, 45):
            sn_dir, scent  = self.sniff_in_dir(angle, sniffing_trail)
            if (current_strength == 0 and scent > 0) or (current_strength > 0 and scent > current_strength):
                found_trail = True
                self.speed = sn_dir

        # keep on wandering
        if not found_trail:
            CHANCE_OF_ANT_DIR_CHANGE = 10 # 1 in 10
            if random.randint(0, CHANCE_OF_ANT_DIR_CHANGE) == 0:
                self.speed = self.speed.rotate(random.choice([-45, 45]))
        self.location = pygame.math.Vector2(self.location.x + self.speed.x, self.location.y + self.speed.y)
        if self.food_strength > 10:
            self.food_strength *= 0.99
        elif self.food_strength > 0:
            self.food_strength -= 1
        if self.nest_strength > 10:
            self.nest_strength *= 0.99
        if self.nest_strength > 0:
            self.nest_strength -= 1


    def collision(self, other):
        if isinstance(other, Food):
            self.found_food = True
            self.food_strength = 100
        if other is self.nest:
            if self.found_food:
                self.speed = self.speed.rotate(180)
            self.found_food = False
            self.nest_strength = 100
        else:
            self.speed = self.speed.rotate(180)

        # self.location = pygame.math.Vector2(self.location.x + self.speed.x, self.location.y + self.speed.y)
        # self.location = pygame.math.Vector2(self.location.x + self.speed.x, self.location.y + self.speed.y)


class Nest:
    def __init__(self, location: pygame.math.Vector2, size=20, population_limit=255) -> None:
        self.location = location
        self.size = size
        self.ants = []
        self.population_limit = population_limit
        self.size_sq = self.size * self.size

    def spawn_ant(self):
        self.ants.append(Ant(self.location, self))

    def draw(self, surface):
        pygame.draw.circle(surface, nest_colour, self.location, self.size)
        [ant.draw(surface) for ant in self.ants]

    def update(self):
        CHANCE_OF_ANT_SPAWN = 3
        if len(self.ants) < self.population_limit and random.randint(0, CHANCE_OF_ANT_SPAWN) == 0:
            self.spawn_ant()

    def collide(self, location):
        return self.location.distance_squared_to(location) < self.size_sq


nest = Nest(pygame.math.Vector2(200, 200), population_limit=255)
border = Border(screen.get_rect())
food = Food(pygame.math.Vector2(400, 100))
food_trail = PheremoneField(food_trail_colour, screen)
nest_trail = PheremoneField(nest_trail_colour, screen)


def draw():
    screen.fill(background_colour)
       
    border.draw(screen)
    food.draw(screen)
    nest.draw(screen)
    food_trail.draw(screen)
    nest_trail.draw(screen)
    pygame.display.flip()


def update():
    nest.update()
    food_trail.update()
    food_trail.add_pheremone(food.location, 1)
    nest_trail.update()
    nest_trail.add_pheremone(nest.location, 1)

    for ant in nest.ants:
        ant.update(food_trail, nest_trail)
        if border.collide(ant.location):
            ant.collision(border)
        if food.collide(ant.location):
            ant.collision(food)
        if nest.collide(ant.location):
            ant.collision(nest)
        if ant.found_food:
            food_trail.add_pheremone(ant.location, ant.food_strength / 100)
        else:
            nest_trail.add_pheremone(ant.location, ant.nest_strength / 100)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            sys.exit()
    update()
    draw()
