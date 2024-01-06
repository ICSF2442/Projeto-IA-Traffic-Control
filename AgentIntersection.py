import spade
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import math
import turtle

from main import intersections


class AgentIntersection(Agent):
    north = int
    south = int

    west = int
    east = int

    carros = []

    class MyBehav(CyclicBehaviour):

        async def change_traffic_lights(self, direction):
            # Change the traffic lights based on the chosen direction
            if direction == "north":
                self.semaforoNorte.setCor("Verde")
                self.semaforoSul.setCor("Vermelho")
                self.semaforoOeste.setCor("Vermelho")
                self.semaforoEste.setCor("Vermelho")
            elif direction == "south":
                self.semaforoNorte.setCor("Vermelho")
                self.semaforoSul.setCor("Verde")
                self.semaforoOeste.setCor("Vermelho")
                self.semaforoEste.setCor("Vermelho")
            elif direction == "east":
                self.semaforoNorte.setCor("Vermelho")
                self.semaforoSul.setCor("Vermelho")
                self.semaforoOeste.setCor("Vermelho")
                self.semaforoEste.setCor("Verde")
            elif direction == "west":
                self.semaforoNorte.setCor("Vermelho")
                self.semaforoSul.setCor("Vermelho")
                self.semaforoOeste.setCor("Verde")
                self.semaforoEste.setCor("Vermelho")

        def check_if_car(self, tag):
            if tag not in self.carros:
                self.carros += [tag]  # Using the += operator to extend the array
                return 0
            else:
                return 1

        def traffic_handler(self):
            max_wait_time = 5  # Define the maximum wait time for fairness (in seconds), adjust as needed
            traffic = {
                "north": self.north,
                "south": self.south,
                "east": self.east,
                "west": self.west
            }

            # Calculate the total number of cars waiting
            total_waiting = sum(traffic.values())

            # Calculate the average wait time per direction (avoid division by zero)
            average_wait_time = {side: max_wait_time if traffic[side] == 0 else self.get_wait_time(side) / traffic[side]
                                 for side in traffic}

            # Calculate a weighted value for each direction considering both traffic and wait time
            weighted_values = {side: traffic[side] * average_wait_time[side] for side in traffic}

            # Select the direction with the highest weighted value
            chosen_direction = max(weighted_values, key=weighted_values.get)

            return chosen_direction

        def get_wait_time(self, direction):
            # Define a function to get the wait time for a specific direction
            if direction == "north":
                return self.north_wait_time
            elif direction == "south":
                return self.south_wait_time
            elif direction == "east":
                return self.east_wait_time
            elif direction == "west":
                return self.west_wait_time
            else:
                return 0  # Return 0 for an unknown direction

        def predict_car_pos(self, carX, carY, direction):
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

        def __init__(self, positionX: int, positionY: int, semaforoNorte: Agent, semaforoSul: Agent,
                     semaforoEste: Agent,
                     semaforoOeste: Agent):
            super().__init__()
            self.south = 0
            self.north = 0
            self.east = 0
            self.west = 0
            self.carros = []
            self.acidente = None
            self.south_wait_time = 0
            self.north_wait_time = 0
            self.east_wait_time = 0
            self.west_wait_time = 0
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

        async def run(self):
            while True:
                responseTotal = await self.receive(timeout=1)
                if responseTotal:
                    if responseTotal.body.startswith("PASSED"):
                        parts = responseTotal.body.split(";")
                        if self.check_if_car(parts[1]) == 1:
                            self.carros -= parts[1]
                            semaforo = self.predict_car_pos(int(parts[2]), int(parts[3]), parts[4])
                            if semaforo == "norte":
                                self.north -= 1
                            elif semaforo == "sul":
                                self.south -= 1
                            elif semaforo == "este":
                                self.east -= 1
                            elif semaforo == "oeste":
                                self.west -= 1
                    if responseTotal.body.startswith("BEACON"):
                        print("recebi o beacon")
                        parts = responseTotal.body.split(";")
                        if len(parts) == 6:
                            car_posX = int(parts[2])
                            car_posY = int(parts[3])
                            car_direction = parts[4]
                            car_agent_jid = parts[5]
                            semaforo = self.predict_car_pos(car_posX, car_posY, car_direction)
                            if semaforo:
                                self.check_if_car(parts[1])
                                msg = Message(to=f"{car_agent_jid}")
                                msg.set_metadata("performative", "agree")
                                msg.body = f"RECIEVED;{self.positionX};{self.positionY};{self.agent.jid}"
                                if semaforo == "norte":
                                    self.north += 1
                                # msg = Message(to=f"{car_agent_jid}")
                                # msg.set_metadata("performative", "agree")
                                # msg.body = f"SEMAFORO;{self.semaforoNorte.cor};{self.semaforoNorte.positionX};{self.semaforoNorte.positionY}"
                                # await self.send(msg)
                                elif semaforo == "sul":
                                    self.south += 1
                                elif semaforo == "este":
                                    self.east += 1
                                elif semaforo == "oeste":
                                    self.west += 1

                await asyncio.sleep(1)

    def __init__(self, jid: str, password: str, positionX, positionY, semaforoNorte: Agent, semaforoSul: Agent,
                 semaforoEste: Agent, semaforoOeste: Agent, verify_security: bool = False):
        super().__init__(jid, password, verify_security)
        self.semaforoNorte = semaforoNorte
        self.semaforoSul = semaforoSul
        self.semaforoOeste = semaforoOeste
        self.semaforoEste = semaforoEste
        self.my_behav = None
        self.positionX = positionX
        self.positionY = positionY
        self.carros = None
        self.west = 0
        self.east = 0
        self.south = 0
        self.north = 0
        self.south_wait_time = 0
        self.north_wait_time = 0
        self.east_wait_time = 0
        self.west_wait_time = 0
        semaforoNorte.setPosicao(self.positionX - 1, self.positionY + 1)
        semaforoNorte.setCor("Verde")
        semaforoSul.setPosicao(self.positionX + 1, self.positionY - 1)
        semaforoSul.setCor("Verde")
        semaforoOeste.setPosicao(self.positionX - 1, self.positionY - 1)
        semaforoEste.setPosicao(self.positionX + 1, self.positionY + 1)

        intersections.append(self)

    async def setup(self):
        print("Interseção na posição ({}, {})".format(self.positionX, self.positionY))
        self.my_behav = self.MyBehav(self.positionX, self.positionY, self.semaforoNorte, self.semaforoSul,
                                     self.semaforoOeste, self.semaforoEste)
        self.add_behaviour(self.my_behav)
