# Importa as bibliotecas necessárias
import spade
from SharedSpace import SharedSpace
from AgentCar import AgentCar
from AgentIntersection import AgentIntersection
from AgentTrafficLight import AgentTrafficLight
from Intersections import Intersections
from WaitingTimeManager import WaitingTimeManager
from EventHandler import EventHandler
import pygame

# Inicializa o pygame
pygame.init()

# Constantes
WIDTH, HEIGHT = 1000, 1000
FPS = 60
WHITE = (255, 255, 255)
GRID_SIZE = 8

# Cria a janela do pygame
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Projeto AI - Controlo de Tráfego")
programIcon = pygame.image.load('images/icon.png')
pygame.display.set_icon(programIcon)
car_agents = {}

# Carrega a imagem de fundo
background_image = pygame.image.load("images/intersecao2.png")
background_rect = background_image.get_rect()

# Carrega as imagens dos carros
car_image = pygame.image.load("images/carro.png")
ambulancia_image = pygame.image.load("images/ambulancia.png")
policia_image = pygame.image.load("images/policia.png")

# Carrega as imagens dos semáforos
green_light_image = pygame.image.load("images/VERDE.png")
red_light_image = pygame.image.load("images/VERMELHO.png")

# Define o tamanho das imagens dos semáforos
light_size = (int(green_light_image.get_width() * 0.1), int(green_light_image.get_height() * 0.1))
green_light_image = pygame.transform.scale(green_light_image, light_size)
red_light_image = pygame.transform.scale(red_light_image, light_size)

# Dicionários para armazenar carros e semáforos na interface
lista_carros_interface = {}
lista_semaforos_interface = {}


# Função para converter coordenadas de grade para posição na tela
def grid_to_screen_position(x, y):
    return x * (WIDTH // GRID_SIZE), y * (HEIGHT // GRID_SIZE)


# Funções para converter coordenadas de grade para posição na tela e vice-versa
def grid_to_x(x):
    return x * (WIDTH // GRID_SIZE)


def grid_to_y(y):
    return y * (HEIGHT // GRID_SIZE)


def screen_position_to_grid(x, y):
    return x // (WIDTH // GRID_SIZE), y // (HEIGHT // GRID_SIZE)


# Classe que representa um semáforo
class TrafficLight:
    lights = []

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.green_light = False  # Estado inicial
        TrafficLight.lights.append(self)

    def switch_light(self):
        self.green_light = not self.green_light

    def green(self):
        if not self.green_light:
            self.green_light = not self.green_light

    def red(self):
        if self.green_light:
            self.green_light = not self.green_light

    def update(self):
        self.switch_light()

    def draw(self, screen):
        light_image = green_light_image if self.green_light else red_light_image
        screen.blit(light_image, (self.x - light_size[0] // 2, self.y - light_size[1] // 2))


# Classe que representa um carro
class Car:
    cars = []

    def __init__(self, tag, start_x, start_y, initial_angle, direction):
        self.tag = tag
        self.image = car_image
        if self.tag == "112":
            self.image = ambulancia_image
        if self.tag == "911":
            self.image = policia_image
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


# Função para atualizar a ‘interface’ gráfica
def update_interface():
    screen.blit(background_image, background_rect)
    # Desenha a imagem de fundo

    for light in TrafficLight.lights:
        light.draw(screen)  # Desenha os semáforos
    for car in Car.cars:
        car.draw(screen)  # Desenha os carros

    for x in range(0, WIDTH, WIDTH // GRID_SIZE):
        pygame.draw.line(screen, (0, 0, 0), (x, 0), (x, HEIGHT))  # Desenha as linhas da grade
    for y in range(0, HEIGHT, HEIGHT // GRID_SIZE):
        pygame.draw.line(screen, (0, 0, 0), (0, y), (WIDTH, y))
    pygame.display.flip()  # Atualiza a tela


# Função de callback para atualizar o semáforo na ‘interface’
def main_semaforo_update(info):
    for i in range(4):
        if i == 0:
            if info[i] == "Verde":
                lista_semaforos_interface["norte"].green()
            else:
                lista_semaforos_interface["norte"].red()
        elif i == 1:
            if info[i] == "Verde":
                lista_semaforos_interface["sul"].green()
            else:
                lista_semaforos_interface["sul"].red()
        elif i == 2:
            if info[i] == "Verde":
                lista_semaforos_interface["oeste"].green()
            else:
                lista_semaforos_interface["oeste"].red()
        elif i == 3:
            if info[i] == "Verde":
                lista_semaforos_interface["este"].green()
            else:
                lista_semaforos_interface["este"].red()

    update_interface()


# Função de callback para atualizar a posição do carro na ‘interface’
def main_callback(info):
    if info in lista_carros_interface:
        lista_carros_interface[info].move_from_message()
        update_interface()


# Função principal assíncrona
async def main():
    global green_light_image, red_light_image
    event_handler = EventHandler()

    # Cria objetos de semáforo
    west_traffic_light = TrafficLight(*grid_to_screen_position(3, 5))
    north_traffic_light = TrafficLight(*grid_to_screen_position(3, 3))
    east_traffic_light = TrafficLight(*grid_to_screen_position(5, 3))
    south_traffic_light = TrafficLight(*grid_to_screen_position(5, 5))

    # Cria objetos de carro
    car_001 = Car("001", 4.5, 8.5, 180, "up")
    car_002 = Car("002", 4.5, 9.5, 180, "up")
    car_003 = Car("003", -1.5, 4.5, 90, "right")
    car_004 = Car("112", 9.5, 3.5, 270, "left")
    # Adiciona os carros e semáforos aos dicionários da interface
    lista_carros_interface[car_001.tag] = car_001
    lista_carros_interface[car_002.tag] = car_002
    lista_carros_interface[car_003.tag] = car_003
    lista_carros_interface[car_004.tag] = car_004
    lista_semaforos_interface["oeste"] = west_traffic_light
    lista_semaforos_interface["norte"] = north_traffic_light
    lista_semaforos_interface["este"] = east_traffic_light
    lista_semaforos_interface["sul"] = south_traffic_light

    # Configuração inicial da ‘interface’
    clock = pygame.time.Clock()

    update_interface()

    # Define o limite de quadros por segundo
    event_handler = EventHandler()
    clock.tick(FPS)
    shared_space = SharedSpace()
    intersections = Intersections()
    waiting_time = WaitingTimeManager()
    event_handler.add_listener(0, main_callback)
    event_handler.add_listener(1, main_semaforo_update)

    # Inicializa os agentes
    semaforo1 = AgentTrafficLight("semaforo1@localhost", "123", positionX=2, positionY=6, cor="Vermelho")
    semaforo2 = AgentTrafficLight("semaforo2@localhost", "123", positionX=2, positionY=6, cor="Vermelho")
    semaforo3 = AgentTrafficLight("semaforo3@localhost", "123", positionX=2, positionY=6, cor="Vermelho")
    semaforo4 = AgentTrafficLight("semaforo4@localhost", "123", positionX=2, positionY=6, cor="Vermelho")
    intersection = AgentIntersection("intersection@localhost", "123", positionX=4, positionY=4, semaforoNorte=semaforo1,
                                     semaforoSul=semaforo2, semaforoEste=semaforo3, semaforoOeste=semaforo4,
                                     intersections=intersections, waiting_time_manager=waiting_time,
                                     event_handler=event_handler)

    carro = AgentCar("carro@localhost", "123", position_x=5, position_y=-1, direction="up", tag="001",
                     shared_space=shared_space, intersections=intersections, waiting_time_manager=waiting_time,
                     event_handler=event_handler)

    carro2 = AgentCar("carro2@localhost", "123", position_x=5, position_y=-2, direction="up", tag="002",
                      shared_space=shared_space, intersections=intersections, waiting_time_manager=waiting_time,
                      event_handler=event_handler)

    carro3 = AgentCar("carro3@localhost", "123", position_x=-1, position_y=3, direction="right", tag="003",
                      shared_space=shared_space, intersections=intersections, waiting_time_manager=waiting_time,
                      event_handler=event_handler)

    carro4 = AgentCar("carro4@localhost", "123", position_x=9, position_y=5, direction="left", tag="112",
                      shared_space=shared_space, intersections=intersections, waiting_time_manager=waiting_time,
                      event_handler=event_handler)

    await intersection.start(auto_register=True)
    await carro.start(auto_register=True)
    car_agents["001"] = carro
    await carro2.start(auto_register=True)
    car_agents["002"] = carro2
    await carro3.start(auto_register=True)
    car_agents["003"] = carro3
    await carro4.start(auto_register=True)
    car_agents["112"] = carro4




# Executa a função principal assíncrona
if __name__ == "__main__":
    spade.run(main())
