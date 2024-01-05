import spade
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import math
import turtle


class AgentTrafficLight(Agent):

    def setPosicao(self, X: int, Y: int):
        self.positionX = X
        self.positionY = Y

    def setCor(self, cor):
        self.cor = cor

    class MyBehav(CyclicBehaviour):
        def __init__(self, positionX, positionY, cor):
            super().__init__()
            self.cor = cor
            self.positionX = positionX
            self.positionY = positionY
            self.contador = 0

        async def run(self):
            while True:

                self.contador = self.contador + 1
                if self.contador == 4:
                    if self.cor == "Vermelho":
                        self.cor = "Verde"
                    else:
                        self.cor = "Vermelho"
                    self.contador = 0

                await asyncio.sleep(1)

    def __init__(self, jid: str, password: str, positionX, positionY, cor, verify_security: bool = False):
        super().__init__(jid, password, verify_security)
        self.cor = cor
        self.my_behav = None
        self.positionX = positionX
        self.positionY = positionY

    async def setup(self):

        print("Semaforo na posição ({}, {}) está: {}".format(self.positionX, self.positionY, "Vermelho"))
        self.my_behav = self.MyBehav(self.positionX, self.positionY, self.cor)
        self.add_behaviour(self.my_behav)
