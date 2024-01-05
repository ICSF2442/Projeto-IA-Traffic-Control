import spade
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import math
import turtle

from main import intersections


class AgentCar(Agent):
    class MyBehav(CyclicBehaviour):
        def __init__(self, positionX, positionY, direction, tag):
            super().__init__()
            self.tag = tag
            self.posicaoX = positionX
            self.posicaoY = positionY
            self.parado = False
            self.direction = direction

        async def run(self):
            counter = 0

            async def beaconSender(counter):
                if counter == 2:
                    for intersection in intersections:
                        distance = math.sqrt((self.posicaoX - intersection.positionX) ** 2 +
                                             (self.posicaoY - intersection.positionY) ** 2)
                        if distance <= 5:
                            beacon_msg = Message(to=f"{intersection.jid}")
                            beacon_msg.set_metadata("performative", "agree")
                            beacon_msg.body = f"BEACON;{self.tag};{self.posicaoX};{self.posicaoY};{self.direction};{self.agent.jid}"
                            print("mandei beacon")
                            await self.send(beacon_msg)
                            print("teste")

            while True:
                if not self.parado:
                    counter = counter + 1
                    await beaconSender(counter)
                    if counter == 2: counter = 0

                    if self.direction == "up":
                        self.posicaoY += 1
                    if self.direction == "down":
                        self.posicaoY -= 1
                    if self.direction == "left":
                        self.posicaoX -= 1
                    if self.direction == "right":
                        self.posicaoX += 1

                    # Check traffic light status

                    response = await self.receive(timeout=1)
                    if response:
                        parts = response.body.split(";")
                        if len(parts) == 3:
                            semaforo_positionX = int(parts[1])
                            semaforo_positionY = int(parts[2])
                            if semaforo_positionX == self.posicaoX and semaforo_positionY == self.posicaoY:
                                if parts[0] == "Verde":
                                    self.parado = False
                                else:
                                    self.parado = True

                    else:
                        print("Nao recebi mensagem mas andei na mesma")
                        if not self.parado:

                            if self.direction == "up":
                                self.posicaoY += 1
                            if self.direction == "down":
                                self.posicaoY -= 1
                            if self.direction == "left":
                                self.posicaoX -= 1
                            if self.direction == "right":
                                self.posicaoX += 1

                    print("Carro na posição superior direita ({}, {})".format(self.posicaoX, self.posicaoY))


                else:
                    print("Carro parado na posição superior direita ({}, {})".format(self.posicaoX, self.posicaoY))

                # Sleep to simulate continuous movement
                await asyncio.sleep(1)

        async def on_end(self):
            print("Comportamento encerrado com código de saída {}.".format(self.exit_code))

    def __init__(self, jid: str, password: str, positionX, positionY, direction, tag: str, verify_security: bool = False):
        super().__init__(jid, password, verify_security)
        self.directon = direction
        self.my_behav = None
        self.posicaoX = positionX
        self.posicaoY = positionY
        self.tag = tag

    async def setup(self):
        print("Agente começando na posição ({}, {})...".format(self.posicaoX, self.posicaoY))
        self.my_behav = self.MyBehav(self.posicaoX, self.posicaoY, self.directon)
        self.add_behaviour(self.my_behav)
