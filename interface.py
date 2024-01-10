import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
FPS = 60
WHITE = (255, 255, 255)

# Create the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Projeto AI - Controlo de Tráfego")
programIcon = pygame.image.load('images/icon.png')
pygame.display.set_icon(programIcon)

# Load background image
background_image = pygame.image.load("images/intersecao.png")  # Replace with your image file
background_rect = background_image.get_rect()

# Load car images
left_car_image = pygame.image.load("images/carro.png")  # Replace with the path to your left car image
top_car_image = pygame.image.load("images/carro.png")  # Replace with the path to your top car image
right_car_image = pygame.image.load("images/carro.png")  # Replace with the path to your right car image
bottom_car_image = pygame.image.load("images/carro.png")  # Replace with the path to your bottom car image

# Load traffic light images
green_light_image = pygame.image.load("images/VERDE.png")  # Replace with the path to your green light image
red_light_image = pygame.image.load("images/VERMELHO.png")  # Replace with the path to your red light image

# Resize traffic light images (20% bigger)
light_size = (int(green_light_image.get_width() * 0.1), int(green_light_image.get_height() * 0.1))
green_light_image = pygame.transform.scale(green_light_image, light_size)
red_light_image = pygame.transform.scale(red_light_image, light_size)

# Create car objects
left_car_rect = left_car_image.get_rect()
left_car_rect.topleft = (WIDTH - 585, HEIGHT // 2 + 10)
left_car_angle = 90  # Initial angle

top_car_rect = top_car_image.get_rect()
top_car_rect.topleft = (WIDTH - 655 // 2 - 20, 15)
top_car_angle = 0  # Initial angle

right_car_rect = right_car_image.get_rect()
right_car_rect.topleft = (WIDTH - 50, HEIGHT // 2 - 45)
right_car_angle = 270  # Initial angle

bottom_car_rect = bottom_car_image.get_rect()
bottom_car_rect.topleft = (WIDTH - 535 // 2 - 20, HEIGHT - 50)
bottom_car_angle = 180  # Initial angle

# Traffic light class
class TrafficLight:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.green_light = True  # Initial state
        self.timer = 0

    def switch_light(self):
        self.green_light = not self.green_light

    def update(self):
        # Change state every 60 frames (1 second)
        if self.timer == 60:
            self.switch_light()
            self.timer = 0
        else:
            self.timer += 1

    def draw(self, screen):
        light_image = green_light_image if self.green_light else red_light_image
        screen.blit(light_image, (self.x - light_size[0] // 2, self.y - light_size[1] // 2))

# Create traffic light objects
left_traffic_light = TrafficLight(230, HEIGHT // 2 + 50)
top_traffic_light = TrafficLight(WIDTH // 2 - 70, 215)
right_traffic_light = TrafficLight(WIDTH - 230, HEIGHT // 2 - 85)
bottom_traffic_light = TrafficLight(WIDTH // 2 + 70, HEIGHT - 250)

# Set rotation speed
rotation_speed = 5

# Main game loop
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Move cars by 5 pixels per click
                left_car_rect.x += 5
                top_car_rect.y += 5
                right_car_rect.x -= 5
                bottom_car_rect.y -= 5
            elif event.key == pygame.K_LEFT:
                # Rotate left car counterclockwise
                left_car_angle += rotation_speed
            elif event.key == pygame.K_RIGHT:
                # Rotate left car clockwise
                left_car_angle -= rotation_speed

    # Update traffic lights
    left_traffic_light.update()
    top_traffic_light.update()
    right_traffic_light.update()
    bottom_traffic_light.update()

    # Clear the screen
    screen.fill(WHITE)

    # Draw the background image
    screen.blit(background_image, background_rect)

    # Draw traffic lights
    left_traffic_light.draw(screen)
    top_traffic_light.draw(screen)
    right_traffic_light.draw(screen)
    bottom_traffic_light.draw(screen)

    # Rotate and draw left car
    rotated_left_car = pygame.transform.rotate(left_car_image, left_car_angle)
    left_car_rect = rotated_left_car.get_rect(center=left_car_rect.center)
    screen.blit(rotated_left_car, left_car_rect.topleft)

    # Rotate and draw top car
    rotated_top_car = pygame.transform.rotate(top_car_image, top_car_angle)
    top_car_rect = rotated_top_car.get_rect(center=top_car_rect.center)
    screen.blit(rotated_top_car, top_car_rect.topleft)

    # Rotate and draw right car
    rotated_right_car = pygame.transform.rotate(right_car_image, right_car_angle)
    right_car_rect = rotated_right_car.get_rect(center=right_car_rect.center)
    screen.blit(rotated_right_car, right_car_rect.topleft)

    # Rotate and draw bottom car
    rotated_bottom_car = pygame.transform.rotate(bottom_car_image, bottom_car_angle)
    bottom_car_rect = rotated_bottom_car.get_rect(center=bottom_car_rect.center)
    screen.blit(rotated_bottom_car, bottom_car_rect.topleft)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)
