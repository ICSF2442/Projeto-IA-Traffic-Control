import socket

import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 1000
FPS = 60
WHITE = (255, 255, 255)

# Create the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Projeto AI - Controlo de Tráfego")
programIcon = pygame.image.load('images/icon.png')
pygame.display.set_icon(programIcon)

# Load background image
background_image = pygame.image.load("images/intersecao2.png")  # Replace with your image file
background_rect = background_image.get_rect()

# Load car images
car_image = pygame.image.load("images/carro.png")  # Replace with the path to your car image

# Load traffic light images
green_light_image = pygame.image.load("images/VERDE.png")  # Replace with the path to your green light image
red_light_image = pygame.image.load("images/VERMELHO.png")  # Replace with the path to your red light image

# Resize traffic light images (20% bigger)
light_size = (int(green_light_image.get_width() * 0.1), int(green_light_image.get_height() * 0.1))
green_light_image = pygame.transform.scale(green_light_image, light_size)
red_light_image = pygame.transform.scale(red_light_image, light_size)


class Car:
    cars = []

    def __init__(self, tag, start_x, start_y, initial_angle=0):
        self.tag = tag
        self.image = car_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (start_x, start_y)
        self.angle = initial_angle
        Car.cars.append(self)

    def update_position(self, x_change, y_change):
        self.rect.x += x_change
        self.rect.y += y_change

    def draw(self, screen):
        rotated_car = pygame.transform.rotate(self.image, self.angle)
        rotated_rect = rotated_car.get_rect(center=self.rect.center)
        screen.blit(rotated_car, rotated_rect.topleft)

    def move_from_message(self):
        x_change, y_change = grid_to_screen_position(1, 0)
        self.update_position(x_change, y_change)

    def listen_for_socket_message(self):
        host = 'localhost'  # Replace with your actual values
        port = 12345

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

        while True:
            message = client_socket.recv(1024).decode()
            if message.startswith(f"MOVED;{self.tag}"):
                self.move_from_message()

class TrafficLight:
    lights = []

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.green_light = False  # Initial state
        TrafficLight.lights.append(self)

    def switch_light(self):
        self.green_light = not self.green_light

    def update(self):
        self.switch_light()

    def draw(self, screen):
        light_image = green_light_image if self.green_light else red_light_image
        screen.blit(light_image, (self.x - light_size[0] // 2, self.y - light_size[1] // 2))


GRID_SIZE = 8  # Number of squares in the grid


def grid_to_screen_position(x, y):
    return x * (WIDTH // GRID_SIZE), y * (HEIGHT // GRID_SIZE)


def screen_position_to_grid(x, y):
    return x // (WIDTH // GRID_SIZE), y // (HEIGHT // GRID_SIZE)


# Create traffic light objects
west_traffic_light = TrafficLight(*grid_to_screen_position(3, 5))
north_traffic_light = TrafficLight(*grid_to_screen_position(3, 3))
east_traffic_light = TrafficLight(*grid_to_screen_position(5, 3))
south_traffic_light = TrafficLight(*grid_to_screen_position(5, 5))

# Create car objects
car_001 = Car("001", *grid_to_screen_position(0.5, 4.5), 90)

car_001.listen_for_socket_message()
# Main game loop
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Move cars by 1 grid unit per click
                for car in Car.cars:
                    car.update_position(*grid_to_screen_position(1, 0))
                for light in TrafficLight.lights:
                    light.update()

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
    clock.tick(FPS)
