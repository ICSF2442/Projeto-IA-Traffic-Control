import spade
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import math
import turtle


class AgentIntersection(Agent):
    class MyBehav(CyclicBehaviour):

        def search_array_of_arrays(self, arrays, item):
            for sub_array in arrays:
                if item in sub_array:
                    return sub_array  # Return the sub-array if the item is found
            return None  # Return None if the item is not found in any sub-array

        async def change_traffic_lights(self, direction):
            if not self.busy:
                # Change the traffic lights based on the chosen direction
                if direction == "north":
                    self.semaforoNorte.setCor("Verde")
                    self.semaforoSul.setCor("Vermelho")
                    self.semaforoOeste.setCor("Vermelho")
                    self.semaforoEste.setCor("Vermelho")
                    self.priorityLine = "north"
                elif direction == "south":
                    self.semaforoNorte.setCor("Vermelho")
                    self.semaforoSul.setCor("Verde")
                    self.semaforoOeste.setCor("Vermelho")
                    self.semaforoEste.setCor("Vermelho")
                    self.priorityLine = "south"

                elif direction == "east":
                    self.semaforoNorte.setCor("Vermelho")
                    self.semaforoSul.setCor("Vermelho")
                    self.semaforoOeste.setCor("Vermelho")
                    self.semaforoEste.setCor("Verde")
                    self.priorityLine = "east"

                elif direction == "west":
                    self.semaforoNorte.setCor("Vermelho")
                    self.semaforoSul.setCor("Vermelho")
                    self.semaforoOeste.setCor("Verde")
                    self.semaforoEste.setCor("Vermelho")
                    self.priorityLine = "west"

        def check_if_car(self, tag):
            if tag not in self.carros:
                self.carros += [tag]  # Using the += operator to extend the array
                return 0
            else:
                return 1

        def traffic_handler(self):
            max_wait_time = 10  # Define the maximum wait time for fairness (in seconds), adjust as needed
            traffic = {
                "north": self.north,
                "south": self.south,
                "east": self.east,
                "west": self.west
            }
            if any(value > 0 for value in traffic.values()):
                # Calculate the total number of cars waiting
                total_waiting = sum(traffic.values())

                # Calculate the average wait time per direction (avoid division by zero)
                average_wait_time = {
                    side: max_wait_time if traffic[side] == 0 else self.get_wait_time(side) / traffic[side]
                    for side in traffic}

                # Calculate a weighted value for each direction considering both traffic and wait time
                weighted_values = {side: traffic[side] * average_wait_time[side] for side in traffic}

                # Select the direction with the highest weighted value
                chosen_direction = max(weighted_values, key=weighted_values.get)

                return chosen_direction

        def get_wait_time(self, direction):

            # Define a function to get the wait time for a specific direction
            if direction == "north":
                self.north_wait_time += self.waiting_time_manger.get_time_for_direction(direction)
                return self.north_wait_time
            elif direction == "south":
                self.south_wait_time += self.waiting_time_manger.get_time_for_direction(direction)
                return self.south_wait_time
            elif direction == "east":
                self.east_wait_time += self.waiting_time_manger.get_time_for_direction(direction)
                return self.east_wait_time
            elif direction == "west":
                self.west_wait_time += self.waiting_time_manger.get_time_for_direction(direction)
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
                     semaforoOeste: Agent, waiting_time_manager):
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

        async def run(self):
            while True:

                await self.change_traffic_lights(self.traffic_handler())
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
                responseTotal = await self.receive(timeout=3)
                if responseTotal:
                    if responseTotal.body.startswith("PASSED"):
                        parts = responseTotal.body.split(";")
                        if self.check_if_car(parts) == 1:
                            self.carros -= parts
                            semaforo = self.predict_car_pos(int(parts[2]), int(parts[3]), parts[4])
                            if int(parts[1]) == 112 or int(parts[1]) == 911:
                                if semaforo == "norte":
                                    self.north -= 25
                                elif semaforo == "sul":
                                    self.south -= 25
                                elif semaforo == "este":
                                    self.east -= 25
                                elif semaforo == "oeste":
                                    self.west -= 25
                            else:
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
                            car_tag = int(parts[1])
                            car_posX = int(parts[2])
                            car_posY = int(parts[3])
                            car_direction = parts[4]
                            car_agent_jid = parts[5]
                            semaforo = self.predict_car_pos(car_posX, car_posY, car_direction)
                            if semaforo:
                                if self.check_if_car(parts) == 0:
                                    self.carrosTAG += str(car_tag)
                                msg = Message(to=f"{car_agent_jid}")
                                msg.set_metadata("performative", "agree")
                                msg.body = f"RECEIVED;{self.positionX};{self.positionY};{self.agent.jid}"
                                await self.send(msg)
                                if car_tag == 112 or car_tag == 911:
                                    if semaforo == "norte":
                                        self.north += 25
                                    elif semaforo == "sul":
                                        self.south += 25
                                    elif semaforo == "este":
                                        self.east += 25
                                    elif semaforo == "oeste":
                                        self.west += 25
                                else:
                                    if semaforo == "norte":
                                        self.north += 1
                                    elif semaforo == "sul":
                                        self.south += 1
                                    elif semaforo == "este":
                                        self.east += 1
                                    elif semaforo == "oeste":
                                        self.west += 1
                for tag in self.carrosTAG:
                    carro = self.search_array_of_arrays(self.carros, tag)
                    car_agent_jid = carro[5]
                    semaforo = self.predict_car_pos(int(carro[2]), int(carro[3]), carro[4])
                    if semaforo == "norte":
                        msg1 = Message(to=f"{car_agent_jid}")
                        msg1.set_metadata("performative", "agree")
                        msg1.body = f"SEMAFORO;{self.semaforoNorte.cor};{self.semaforoNorte.positionX};{self.semaforoNorte.positionY}"
                        await self.send(msg1)
                    elif semaforo == "sul":
                        msg2 = Message(to=f"{car_agent_jid}")
                        msg2.set_metadata("performative", "agree")
                        msg2.body = f"SEMAFORO;{self.semaforoSul.cor};{self.semaforoSul.positionX};{self.semaforoSul.positionY}"
                        await self.send(msg2)
                    elif semaforo == "este":
                        msg3 = Message(to=f"{car_agent_jid}")
                        msg3.set_metadata("performative", "agree")
                        msg3.body = f"SEMAFORO;{self.semaforoEste.cor};{self.semaforoEste.positionX};{self.semaforoEste.positionY}"
                        await self.send(msg3)
                    elif semaforo == "oeste":
                        msg4 = Message(to=f"{car_agent_jid}")
                        msg4.set_metadata("performative", "agree")
                        msg4.body = f"SEMAFORO;{self.semaforoOeste.cor};{self.semaforoOeste.positionX};{self.semaforoOeste.positionY}"
                        await self.send(msg4)
                    await asyncio.sleep(2)
                await asyncio.sleep(1)

    def __init__(self, jid: str, password: str, positionX, positionY, semaforoNorte: Agent, semaforoSul: Agent,
                 semaforoEste: Agent, semaforoOeste: Agent, intersections, waiting_time_manager,
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

    async def setup(self):
        print("Interseção na posição ({}, {})".format(self.positionX, self.positionY))
        self.my_behav = self.MyBehav(self.positionX, self.positionY, self.semaforoNorte, self.semaforoSul,
                                     self.semaforoOeste, self.semaforoEste, self.waiting_time_manager)
        self.add_behaviour(self.my_behav)
