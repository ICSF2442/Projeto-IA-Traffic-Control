import spade
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import math
import turtle


class AgentIntersection(Agent):
    class MyBehav(CyclicBehaviour):

        def search_array_of_arrays(self, arrays,
                                   item):  # Procura um item dentro de um array que está dentro de um array.
            for sub_array in arrays:
                if item in sub_array:
                    return sub_array  # Retorna o sub-array se o objeto for encontrado
            return None  # Retorna None se o item nao for encontrado

        async def change_traffic_lights(self, direction):  # Mudança das luzes dos semaforos baseada na direção recebida

            if not self.busy:

                if direction == "north":

                    self.semaforoNorte.setCor("Verde")
                    self.semaforoSul.setCor("Vermelho")
                    self.semaforoOeste.setCor("Vermelho")
                    self.semaforoEste.setCor("Vermelho")
                    self.priorityLine = "north"
                    estado_semaforos = ["Verde", "Vermelho", "Vermelho", "Vermelho"]
                    self.event_handler.trigger_event(1, estado_semaforos)  # ----> Envia para a Interface o update do
                    # estado dos semaforos
                    print(f"Priority: {self.priorityLine}")
                elif direction == "south":

                    self.semaforoNorte.setCor("Vermelho")
                    self.semaforoSul.setCor("Verde")
                    self.semaforoOeste.setCor("Vermelho")
                    self.semaforoEste.setCor("Vermelho")
                    estado_semaforos = ["Vermelho", "Verde", "Vermelho", "Vermelho"]
                    self.priorityLine = "south"
                    self.event_handler.trigger_event(1, estado_semaforos)
                    print(f"Priority: {self.priorityLine}")

                elif direction == "east":
                    self.semaforoNorte.setCor("Vermelho")
                    self.semaforoSul.setCor("Vermelho")
                    self.semaforoOeste.setCor("Vermelho")
                    self.semaforoEste.setCor("Verde")
                    self.priorityLine = "east"
                    estado_semaforos = ["Vermelho", "Vermelho", "Vermelho", "Verde"]
                    self.event_handler.trigger_event(1, estado_semaforos)
                    print(f"Priority: {self.priorityLine}")

                elif direction == "west":
                    self.semaforoNorte.setCor("Vermelho")
                    self.semaforoSul.setCor("Vermelho")
                    self.semaforoOeste.setCor("Verde")
                    self.semaforoEste.setCor("Vermelho")
                    self.priorityLine = "west"
                    estado_semaforos = ["Vermelho", "Vermelho", "Verde", "Vermelho"]
                    self.event_handler.trigger_event(1, estado_semaforos)
                    print(f"Priority: {self.priorityLine}")


        def check_if_car(self, tag):  # Verifica se o carro existe no array de carros que a interseção recebu
            tag = tag[1:]
            if self.search_array_of_arrays(self.carros, tag[0]) is None:  # Se nao existir, adiciona e retorna 0.
                if tag not in self.carros:
                    self.carros += [tag]  # Using the += operator to extend the array
                    return 0
            else:
                return 1

        # Método para lidar com o tráfego e decidir a direção com base no peso calculado
        def traffic_handler(self):
            max_wait_time = 40  # Define o tempo máximo de espera para equidade (em segundos), ajuste conforme necessário
            traffic = {
                "north": self.north,
                "south": self.south,
                "east": self.east,
                "west": self.west
            }
            if any(value > 0 for value in traffic.values()):

                # Calcular o número total de carros esperando
                total_waiting = sum(traffic.values())

                # Calcular o tempo médio de espera por direção (evitar divisão por zero)
                wait_time = {
                    side: max_wait_time if traffic[side] == 0 else traffic[side] * self.get_wait_time(side)
                    for side in traffic}

                # Calcular um valor ponderado para cada direção considerando tanto o tráfego quanto o tempo de espera
                weighted_values = {side: traffic[side] * wait_time[side] for side in traffic}

                # Selecionar a direção com o valor ponderado mais alto
                chosen_direction = max(weighted_values, key=weighted_values.get)
                return chosen_direction

        def get_wait_time(self, direction):  # Função para obter o tempo de espera dependendo da direção inserida

            if direction == "north":
                self.north_wait_time += self.waiting_time_manger.get_time_for_direction(direction)
                print(f"Tempo de espera da linha norte: {self.north_wait_time}")
                return self.north_wait_time
            elif direction == "south":
                self.south_wait_time += self.waiting_time_manger.get_time_for_direction(direction)
                print(f"Tempo de espera da linha sul: {self.south_wait_time}")
                return self.south_wait_time
            elif direction == "east":
                self.east_wait_time += self.waiting_time_manger.get_time_for_direction(direction)
                print(f"Tempo de espera da linha este: {self.east_wait_time}")
                return self.east_wait_time
            elif direction == "west":
                self.west_wait_time += self.waiting_time_manger.get_time_for_direction(direction)
                print(f"Tempo de espera da linha oeste: {self.west_wait_time}")
                return self.west_wait_time
            else:
                return 0  # Return 0 for an unknown direction

        def predict_car_pos(self, carX, carY,
                            direction):  # Função para prever a posição dos carros e que semaforo vao encontrar
            predicted_direction = None

            if direction == "up" and self.semaforoSul.positionX == carX:
                predicted_direction = "sul"

            elif direction == "down" and self.semaforoNorte.positionX == carX:
                predicted_direction = "norte"

            elif direction == "left" and self.semaforoEste.positionY == carY:
                predicted_direction = "este"

            elif direction == "right" and self.semaforoOeste.positionY == carY:
                predicted_direction = "oeste"

            return predicted_direction

        async def send_traffic_light_info(self):
            # For ‘loop’ para enviar a todos os carros presentes nos dados da intserseção o estado dos semaforos
            # dependendo da sua direção
            for tag in self.carrosTAG:
                carro = self.search_array_of_arrays(self.carros, tag)
                car_agent_jid = carro[4]
                semaforo = self.predict_car_pos(int(carro[1]), int(carro[2]), carro[3])
                if semaforo == "norte":
                    msg1 = Message(to=f"{car_agent_jid}")
                    msg1.set_metadata("performative", "agree")
                    msg1.body = f"SEMAFORO;{self.semaforoNorte.cor};{self.semaforoNorte.positionX};{self.semaforoNorte.positionY + 1}"
                    await self.send(msg1)
                elif semaforo == "sul":
                    msg2 = Message(to=f"{car_agent_jid}")
                    msg2.set_metadata("performative", "agree")
                    msg2.body = f"SEMAFORO;{self.semaforoSul.cor};{self.semaforoSul.positionX};{self.semaforoSul.positionY - 1}"
                    await self.send(msg2)
                elif semaforo == "este":
                    msg3 = Message(to=f"{car_agent_jid}")
                    msg3.set_metadata("performative", "agree")
                    msg3.body = f"SEMAFORO;{self.semaforoEste.cor};{self.semaforoEste.positionX + 1};{self.semaforoEste.positionY}"
                    await self.send(msg3)
                elif semaforo == "oeste":
                    msg4 = Message(to=f"{car_agent_jid}")
                    msg4.set_metadata("performative", "agree")
                    msg4.body = f"SEMAFORO;{self.semaforoOeste.cor};{self.semaforoOeste.positionX - 1};{self.semaforoOeste.positionY}"
                    await self.send(msg4)

        def change_busy_status(self):  # Função para determinar se a interseção está ocupada
            traffic = {
                "north": self.north,
                "south": self.south,
                "east": self.east,
                "west": self.west
            }
            if self.priorityLine in traffic:
                self.busy = traffic[self.priorityLine] > 0
            else:
                self.busy = False

        # Construtor
        def __init__(self, positionX: int, positionY: int, semaforoNorte: Agent, semaforoSul: Agent,
                     semaforoEste: Agent,
                     semaforoOeste: Agent, waiting_time_manager, event_handler):
            super().__init__()
            self.south = 0
            self.north = 0
            self.east = 0
            self.west = 0
            self.carros = []
            self.carrosTAG = []
            self.acidente = None
            self.south_wait_time = 1
            self.north_wait_time = 1
            self.east_wait_time = 1
            self.west_wait_time = 1
            semaforoNorte.setPosicao(positionX - 1, positionY + 1)
            semaforoNorte.setCor("Verde")
            semaforoSul.setPosicao(positionX + 1, positionY - 1)
            semaforoSul.setCor("Verde")
            semaforoOeste.setPosicao(positionX - 1, positionY - 1)
            semaforoEste.setPosicao(positionX + 1, positionY + 1)
            self.semaforoNorte = semaforoNorte
            self.semaforoSul = semaforoSul
            self.semaforoEste = semaforoEste
            self.semaforoOeste = semaforoOeste
            self.positionX = positionX
            self.positionY = positionY
            self.busy = False
            self.priorityLine = None
            self.waiting_time_manger = waiting_time_manager
            self.event_handler = event_handler

        async def run(self):  # Inicializador
            while True:

                await self.change_traffic_lights(self.traffic_handler())  # Atualização do estado dos semaforos
                self.change_busy_status()  # Atualização do estado da interseção se está ocupada ou não
                print(f"Im busy? {self.busy}")
                responseTotal = await self.receive(timeout=3)  # Espera da receção das mensagens
                if responseTotal:
                    if responseTotal.body.startswith(
                            "PASSED"):  # Se receber "PASSED" signfica que um carro passou da interseção
                        # E irá fazer o necessário para remover o carro dos dados da interseção
                        parts = responseTotal.body.split(";")
                        print(f"recebi passed {parts[1]}")
                        if self.check_if_car(parts) == 1:
                            carro = self.search_array_of_arrays(self.carros, parts[1])
                            self.carrosTAG.remove(parts[1])
                            self.carros.remove(carro)
                            semaforo = self.predict_car_pos(int(carro[1]), int(carro[2]), carro[3])
                            if int(parts[1]) == 112 or int(parts[1]) == 911:
                                if semaforo == "norte":
                                    self.north -= 250
                                elif semaforo == "sul":
                                    self.south -= 250
                                elif semaforo == "este":
                                    self.east -= 250
                                elif semaforo == "oeste":
                                    self.west -= 250
                            else:
                                if semaforo == "norte":
                                    self.north -= 1
                                elif semaforo == "sul":
                                    self.south -= 1
                                elif semaforo == "este":
                                    self.east -= 1
                                elif semaforo == "oeste":
                                    self.west -= 1
                        self.change_busy_status()
                        await self.change_traffic_lights(self.traffic_handler())
                    if responseTotal.body.startswith(
                            "BEACON"):  # Se receber "BEACON" signfica que um carro irá chegar à interseção
                        # E irá fazer o necessário para adicionar o carro aos dados da interseção
                        parts = responseTotal.body.split(";")
                        print(f"recebi o beacon {parts[1]}")
                        if len(parts) == 6:
                            car_tag = str(parts[1])
                            car_posX = int(parts[2])
                            car_posY = int(parts[3])
                            car_direction = parts[4]
                            car_agent_jid = parts[5]
                            semaforo = self.predict_car_pos(car_posX, car_posY, car_direction)
                            if semaforo:
                                if self.check_if_car(parts) == 0:
                                    self.carrosTAG.append(car_tag)
                                    msg = Message(to=f"{car_agent_jid}")
                                    msg.set_metadata("performative", "agree")
                                    msg.body = f"RECEIVED;{self.positionX};{self.positionY};{self.agent.jid}"

                                    # Envia a mensagem "RECIEVED" para um carro que
                                    # enviou o "BEACON" para que este saiba que a interseção
                                    # saiba da sua existencia e que este pare de enviar "BEACONs

                                    await self.send(msg)

                                    # Adicionar a presença dos carros a cada direção dependendo da qual ele vem
                                    # Carros de prioridade têm muito maior presença para que estes ganhem a prioridade

                                    if car_tag == "112" or car_tag == "911":
                                        if semaforo == "norte":
                                            self.north += 250
                                        elif semaforo == "sul":
                                            self.south += 250
                                        elif semaforo == "este":
                                            self.east += 250
                                        elif semaforo == "oeste":
                                            self.west += 250

                                    else:
                                        if semaforo == "norte":
                                            self.north += 1
                                        elif semaforo == "sul":
                                            self.south += 1
                                        elif semaforo == "este":
                                            self.east += 1
                                        elif semaforo == "oeste":
                                            self.west += 1
                await self.send_traffic_light_info()

                await asyncio.sleep(1)

    # Construtor
    def __init__(self, jid: str, password: str, positionX, positionY, semaforoNorte: Agent, semaforoSul: Agent,
                 semaforoEste: Agent, semaforoOeste: Agent, intersections, waiting_time_manager, event_handler,
                 verify_security: bool = False):
        super().__init__(jid, password, verify_security)
        self.semaforoNorte = semaforoNorte
        self.semaforoSul = semaforoSul
        self.semaforoOeste = semaforoOeste
        self.semaforoEste = semaforoEste
        self.my_behav = None
        self.positionX = positionX
        self.positionY = positionY
        self.carros = []
        self.carrosTAG = []
        self.west = 0
        self.east = 0
        self.south = 0
        self.north = 0
        self.south_wait_time = 1
        self.north_wait_time = 1
        self.east_wait_time = 1
        self.west_wait_time = 1
        self.busy = False
        self.waiting_time_manager = waiting_time_manager
        semaforoNorte.setPosicao(self.positionX - 1, self.positionY + 1)
        semaforoNorte.setCor("Verde")
        semaforoSul.setPosicao(self.positionX + 1, self.positionY - 1)
        semaforoSul.setCor("Verde")
        semaforoOeste.setPosicao(self.positionX - 1, self.positionY - 1)
        semaforoEste.setPosicao(self.positionX + 1, self.positionY + 1)
        intersections.add_intersection(self)
        self.event_handler = event_handler

    async def setup(self):
        print("Interseção na posição ({}, {})".format(self.positionX, self.positionY))
        self.my_behav = self.MyBehav(self.positionX, self.positionY, self.semaforoNorte, self.semaforoSul,
                                     self.semaforoOeste, self.semaforoEste, self.waiting_time_manager,
                                     self.event_handler)
        self.add_behaviour(self.my_behav)
