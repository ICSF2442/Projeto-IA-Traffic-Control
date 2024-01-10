import time

import spade
import asyncio
from SharedSpace import SharedSpace
from AgentCar import AgentCar
from AgentIntersection import AgentIntersection
from AgentTrafficLight import AgentTrafficLight
from Intersections import Intersections
from WaitingTimeManager import WaitingTimeManager
from EventHandler import EventHandler
import pygame

pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 1000
FPS = 60
WHITE = (255, 255, 255)
GRID_SIZE = 8
# Create the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Projeto AI - Controlo de Tráfego")
programIcon = pygame.image.load('images/icon.png')
pygame.display.set_icon(programIcon)
car_agents = {}

background_image = pygame.image.load("images/intersecao2.png")  # Replace with your image file
background_rect = background_image.get_rect()

# Load car images
car_image = pygame.image.load("images/carro.png")  # Replace with the path to your car image

# Load traffic light images
green_light_image = pygame.image.load("images/VERDE.png")  # Replace with the path to your green light image
red_light_image = pygame.image.load("images/VERMELHO.png")  # Replace with the path to your red light image

light_size = (int(green_light_image.get_width() * 0.1), int(green_light_image.get_height() * 0.1))
green_light_image = pygame.transform.scale(green_light_image, light_size)
red_light_image = pygame.transform.scale(red_light_image, light_size)

lista_carros_interface = {}
lista_semaforos_interface = {}


def grid_to_screen_position(x, y):
    return x * (WIDTH // GRID_SIZE), y * (HEIGHT // GRID_SIZE)


def grid_to_x(x):
    return x * (WIDTH // GRID_SIZE)


def grid_to_y(y):
    return y * (HEIGHT // GRID_SIZE)


def screen_position_to_grid(x, y):
    return x // (WIDTH // GRID_SIZE), y // (HEIGHT // GRID_SIZE)


class TrafficLight:
    lights = []

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.green_light = False  # Initial state
        TrafficLight.lights.append(self)

    def switch_light(self):
        self.green_light = not self.green_light

    def green(self):
        self.green_light = self.green_light

    def red(self):
        self.green_light = not self.green_light
    def update(self):
        self.switch_light()

    def draw(self, screen):
        light_image = green_light_image if self.green_light else red_light_image
        screen.blit(light_image, (self.x - light_size[0] // 2, self.y - light_size[1] // 2))


class Car:
    cars = []

    def __init__(self, tag, start_x, start_y, initial_angle, direction):
        self.tag = tag
        self.image = car_image
        self.rect = self.image.get_rect()
        start_x = grid_to_x(start_x)
        start_y = grid_to_y(start_y)
        self.rect.topleft = (start_x, start_y)
        self.angle = initial_angle
        self.direction = direction
        Car.cars.append(self)

    def update_position(self, x_change, y_change):
        self.rect.x += x_change
        self.rect.y += y_change

    def draw(self, screen):
        rotated_car = pygame.transform.rotate(self.image, self.angle)
        rotated_rect = rotated_car.get_rect(center=self.rect.center)
        screen.blit(rotated_car, rotated_rect.topleft)

    def move_from_message(self):
        if self.direction == "right":
            x_change, y_change = grid_to_screen_position(1, 0)
            self.update_position(x_change, y_change)
        if self.direction == "left":
            x_change, y_change = grid_to_screen_position(-1, 0)
            self.update_position(x_change, y_change)
        if self.direction == "up":
            x_change, y_change = grid_to_screen_position(0, -1)
            self.update_position(x_change, y_change)
        if self.direction == "down":
            x_change, y_change = grid_to_screen_position(0, +1)
            self.update_position(x_change, y_change)


def main_callback(info):
    if info in lista_carros_interface:
        lista_carros_interface[info].move_from_message()
        screen.fill(WHITE)  # Clear the screen
        screen.blit(background_image, background_rect)  # Draw the background image
        for light in TrafficLight.lights:
            light.draw(screen)  # Draw traffic lights
        for car in Car.cars:
            car.draw(screen)  # Draw cars
        for x in range(0, WIDTH, WIDTH // GRID_SIZE):
            pygame.draw.line(screen, (0, 0, 0), (x, 0), (x, HEIGHT))  # Draw grid lines
        for y in range(0, HEIGHT, HEIGHT // GRID_SIZE):
            pygame.draw.line(screen, (0, 0, 0), (0, y), (WIDTH, y))
        pygame.display.flip()  # Update the display



# "001" -> objeto carro

async def main():
    global green_light_image, red_light_image
    event_handler = EventHandler()

    # Initialize Pygame

    # Load background image

    # Resize traffic light images (20% bigger)

    # Number of squares in the grid

    def grid_to_screen_position(x, y):
        return x * (WIDTH // GRID_SIZE), y * (HEIGHT // GRID_SIZE)

    def screen_position_to_grid(x, y):
        return x // (WIDTH // GRID_SIZE), y // (HEIGHT // GRID_SIZE)

    # Create traffic light objects
    west_traffic_light = TrafficLight(*grid_to_screen_position(3, 5))
    north_traffic_light = TrafficLight(*grid_to_screen_position(3, 3))
    east_traffic_light = TrafficLight(*grid_to_screen_position(5, 3))
    south_traffic_light = TrafficLight(*grid_to_screen_position(5, 5))
    car_001 = Car("001", 4.5, 8.5, 180, "up")
    car_002 = Car("002", 4.5, 9.5, 180, "up")
    car_003 = Car("003", -1.5, 4.5, 90, "right")

    lista_carros_interface[car_001.tag] = car_001
    lista_carros_interface[car_002.tag] = car_002
    lista_carros_interface[car_003.tag] = car_003
    lista_semaforos_interface["oeste"] = west_traffic_light
    lista_semaforos_interface["norte"] = north_traffic_light
    lista_semaforos_interface["este"] = east_traffic_light
    lista_semaforos_interface["sul"] = south_traffic_light
    # Main game loop
    clock = pygame.time.Clock()

    # Clear the screen
    screen.fill(WHITE)

    # Draw the background image
    screen.blit(background_image, background_rect)

    # Draw traffic lights
    for light in TrafficLight.lights:
        light.draw(screen)

        # Draw cars
    for car in Car.cars:
        car.draw(screen)

        # Draw grid lines
    for x in range(0, WIDTH, WIDTH // GRID_SIZE):
        pygame.draw.line(screen, (0, 0, 0), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, HEIGHT // GRID_SIZE):
        pygame.draw.line(screen, (0, 0, 0), (0, y), (WIDTH, y))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    event_handler = EventHandler()
    clock.tick(FPS)
    shared_space = SharedSpace()
    intersections = Intersections()
    waiting_time = WaitingTimeManager()
    event_handler.add_listener(0, main_callback)
    semaforo1 = AgentTrafficLight("semaforo1@localhost", "123", positionX=2, positionY=6, cor="Vermelho")
    semaforo2 = AgentTrafficLight("semaforo2@localhost", "123", positionX=2, positionY=6, cor="Vermelho")
    semaforo3 = AgentTrafficLight("semaforo3@localhost", "123", positionX=2, positionY=6, cor="Vermelho")
    semaforo4 = AgentTrafficLight("semaforo4@localhost", "123", positionX=2, positionY=6, cor="Vermelho")
    intersection = AgentIntersection("intersection@localhost", "123", positionX=4, positionY=4, semaforoNorte=semaforo1,
                                     semaforoSul=semaforo2, semaforoEste=semaforo3, semaforoOeste=semaforo4,
                                     intersections=intersections, waiting_time_manager=waiting_time)

    carro = AgentCar("carro@localhost", "123", position_x=5, position_y=-1, direction="up", tag="001",
                     shared_space=shared_space, intersections=intersections, waiting_time_manager=waiting_time,
                     event_handler=event_handler)

    carro2 = AgentCar("carro2@localhost", "123", position_x=5, position_y=-2, direction="up", tag="002",
                      shared_space=shared_space, intersections=intersections, waiting_time_manager=waiting_time,
                      event_handler=event_handler)

    carro3 = AgentCar("carro3@localhost", "123", position_x=-1, position_y=3, direction="right", tag="003",
                      shared_space=shared_space, intersections=intersections, waiting_time_manager=waiting_time,
                      event_handler=event_handler)
    await semaforo1.start(auto_register=True)
    await semaforo2.start(auto_register=True)
    await semaforo3.start(auto_register=True)
    await semaforo4.start(auto_register=True)
    await intersection.start(auto_register=True)
    await carro.start(auto_register=True)
    car_agents["001"] = carro  # Replace "001" with the actual car tag
    await carro2.start(auto_register=True)
    car_agents["002"] = carro2  # Replace "001" with the actual car tag
    await carro3.start(auto_register=True)
    car_agents["003"] = carro3  # Replace "001" with the actual car tag


if __name__ == "__main__":
    spade.run(main())
