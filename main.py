import spade
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import math
import turtle

from AgentCar import AgentCar
from AgentIntersection import AgentIntersection
from AgentTrafficLight import AgentTrafficLight

intersections = []


async def main():
    semaforo1 = AgentTrafficLight("semaforo1@localhost", "123", positionX=2, positionY=6, cor="Vermelho")
    semaforo2 = AgentTrafficLight("semaforo2@localhost", "123", positionX=2, positionY=6, cor="Vermelho")
    semaforo3 = AgentTrafficLight("semaforo3@localhost", "123", positionX=2, positionY=6, cor="Vermelho")
    semaforo4 = AgentTrafficLight("semaforo4@localhost", "123", positionX=2, positionY=6, cor="Vermelho")
    intersection = AgentIntersection("intersection@localhost", "123", positionX=5, positionY=5, semaforoNorte=semaforo1,
                                     semaforoSul=semaforo2, semaforoEste=semaforo3, semaforoOeste=semaforo4)

    carro = AgentCar("carro@localhost", "123", positionX=6, positionY=-4, direction="up", tag="001")

    await semaforo1.start(auto_register=True)
    await semaforo2.start(auto_register=True)
    await semaforo3.start(auto_register=True)
    await semaforo4.start(auto_register=True)
    await intersection.start(auto_register=True)
    await carro.start(auto_register=True)


if __name__ == "__main__":
    spade.run(main())
