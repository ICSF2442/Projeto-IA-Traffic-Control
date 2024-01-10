import spade
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import math
import turtle
from SharedSpace import SharedSpace
from AgentCar import AgentCar
from AgentIntersection import AgentIntersection
from AgentTrafficLight import AgentTrafficLight
from Intersections import Intersections
from WaitingTimeManager import WaitingTimeManager


async def main():
    shared_space = SharedSpace()
    intersections = Intersections()
    waiting_time = WaitingTimeManager()

    semaforo1 = AgentTrafficLight("semaforo1@localhost", "123", positionX=2, positionY=6, cor="Vermelho")
    semaforo2 = AgentTrafficLight("semaforo2@localhost", "123", positionX=2, positionY=6, cor="Vermelho")
    semaforo3 = AgentTrafficLight("semaforo3@localhost", "123", positionX=2, positionY=6, cor="Vermelho")
    semaforo4 = AgentTrafficLight("semaforo4@localhost", "123", positionX=2, positionY=6, cor="Vermelho")
    intersection = AgentIntersection("intersection@localhost", "123", positionX=5, positionY=5, semaforoNorte=semaforo1,
                                     semaforoSul=semaforo2, semaforoEste=semaforo3, semaforoOeste=semaforo4,
                                     intersections=intersections, waiting_time_manager=waiting_time)

    carro = AgentCar("carro@localhost", "123", position_x=6, position_y=0, direction="up", tag="001",
                     shared_space=shared_space, intersections=intersections, waiting_time_manager=waiting_time)

    carro2 = AgentCar("carro2@localhost", "123", position_x=6, position_y=-1, direction="up", tag="002", shared_space=shared_space, intersections=intersections, waiting_time_manager=waiting_time)

    carro3 = AgentCar("carro3@localhost", "123", position_x=0, position_y=4, direction="right", tag="003", shared_space=shared_space, intersections=intersections, waiting_time_manager=waiting_time)
    await semaforo1.start(auto_register=True)
    await semaforo2.start(auto_register=True)
    await semaforo3.start(auto_register=True)
    await semaforo4.start(auto_register=True)
    await intersection.start(auto_register=True)
    await carro.start(auto_register=True)
    await carro2.start(auto_register=True)
    await carro3.start(auto_register=True)


if __name__ == "__main__":
    spade.run(main())
