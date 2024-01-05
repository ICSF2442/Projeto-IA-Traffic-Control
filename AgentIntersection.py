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

        def check_if_car(self, tag):
            if tag not in self.carros:
                self.carros += [tag]  # Using the += operator to extend the array
                return 0
            else:
                return 1

        def traffic_handler(self, tempoNorte, tempoSul, TempoOeste, TempoEste):
            bruh = int

        def predict_car_pos(self, carX, carY, direction):
            if direction == "up":
                if self.semaforoSul.positionX == carX:
                    self.south += 1
                    return "sul"

                else:
                    return None

            elif direction == "down":
                if self.semaforoNorte.positionX == carX:
                    self.north += 1
                    return "norte"
                else:
                    return None

            elif direction == "left":
                if self.semaforoEste.positionY == carY:
                    print("a")
                    self.east += 1
                    return "este"

                else:
                    return None

            elif direction == "right":
                if self.semaforoOeste.positionY == carY:
                    self.west += 1
                    return "oeste"
                else:
                    return None

        def __init__(self, positionX: int, positionY: int, semaforoNorte: Agent, semaforoSul: Agent,
                     semaforoEste: Agent,
                     semaforoOeste: Agent):
            super().__init__()
            self.south = 0
            self.north = 0
            self.east = 0
            self.west = 0
            self.carros = None
            self.acidente = None
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

        async def run(self):
            while True:
                if self.semaforoNorte.cor == "Verde":
                    print("semaforo norte ta verde")
                else:
                    print("semaforo norte ta vermelho")
                responseTotal = await self.receive(timeout=10)
                if responseTotal:
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
                                while True:
                                    if semaforo == "norte":
                                        msg = Message(to=f"{car_agent_jid}")
                                        msg.set_metadata("performative", "agree")
                                        msg.body = f"{self.semaforoNorte.cor};{self.semaforoNorte.positionX};{self.semaforoNorte.positionY}"
                                        await self.send(msg)
                                    elif semaforo == "sul":
                                        msg = Message(to=f"{car_agent_jid}")
                                        msg.set_metadata("performative", "agree")
                                        msg.body = f"{self.semaforoSul.cor};{self.semaforoSul.positionX};{self.semaforoSul.positionY}"
                                        await self.send(msg)
                                    elif semaforo == "este":
                                        msg = Message(to=f"{car_agent_jid}")
                                        msg.set_metadata("performative", "agree")
                                        msg.body = f"{self.semaforoEste.cor};{self.semaforoEste.positionX};{self.semaforoEste.positionY}"
                                        await self.send(msg)
                                    elif semaforo == "oeste":
                                        msg = Message(to=f"{car_agent_jid}")
                                        msg.set_metadata("performative", "agree")
                                        msg.body = f"{self.semaforoOeste.cor};{self.semaforoOeste.positionX};{self.semaforoOeste.positionY}"
                                        await self.send(msg)

                                    await asyncio.sleep(1)

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
