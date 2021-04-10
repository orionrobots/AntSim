import pygame
from pygame import draw
from pygame.math import Vector2
import math
import time


def generate_circle(center: Vector2, radius: int):
    # https://en.wikipedia.org/wiki/Midpoint_circle_algorithm
    # x**2 + y**2 = r ** 2
    x = radius
    y = 0

    sq_x = x ** 2 - (2 * y) - 1
    while sq_x > 0 and x > y:
        x = math.sqrt(sq_x)
        yield center + Vector2(x, y)
        yield center + Vector2(-x, y)
        yield center + Vector2(x, -y)
        yield center + Vector2(-x, -y)
        yield center + Vector2(y, x)
        yield center + Vector2(y, -x)
        yield center + Vector2(-y, x)
        yield center + Vector2(-y, -x)

        try:
            sq_x = sq_x - (2 * y) - 1
            y += 1
        except ValueError:
            print("Error at", x, y)
            raise

def generate_filled_circle(center: Vector2, radius: int):
    # Yield line start + end vectors
    # https://en.wikipedia.org/wiki/Midpoint_circle_algorithm
    # x**2 + y**2 = r ** 2
    x = radius
    y = 0

    sq_x = x ** 2 - (2 * y) - 1
    while sq_x > 0 and x > y:
        x = math.sqrt(sq_x)
        yield center + Vector2(-x, y), center + Vector2(x, y)
        yield center + Vector2(-x, -y), center + Vector2(x, -y)
        yield  center + Vector2(-y, -x), center + Vector2(y, -x)
        yield center + Vector2(-y, x), center + Vector2(y, x)

        sq_x = sq_x - (2 * y) - 1
        y += 1


def main():
    pygame.init()
    screen = pygame.display.set_mode((200, 200))
    draw_color = pygame.Color(255, 255, 255)
    new_draw = pygame.Color(255, 0, 0)
    black = 0, 0, 0
    screen.fill(black)


    pygame.event.get()
    # for rad in range(60, 1, -1):
    #     print(rad)
    #     for point in generate_circle(Vector2(100, 100), rad/2):
    #         screen.set_at((int(point.x), int(point.y)), draw_color)
    #     pygame.display.flip()
    # rad = 8
    # for point in generate_circle(Vector2(100, 100), rad/2):
    #     print(point)
    #     screen.set_at((int(point.x), int(point.y)), draw_color)
    #     pygame.display.flip()
    for start, end in generate_filled_circle(Vector2(100, 100), 40):
        draw.line(screen, new_draw, start, end)
        pygame.display.flip()
        time.sleep(1/20)
        draw.line(screen, draw_color, start, end)
        pygame.display.flip()


    running = True
    while running:
        for event in pygame.event.get():
            

            if event.type == pygame.QUIT:
                running = False
        
if __name__ == "__main__":
    main()
