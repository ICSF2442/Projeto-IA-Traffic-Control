import spade
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import math
import turtle

from main import intersections


class AgentCar(Agent):

    class CarBehavior(CyclicBehaviour):
        def __init__(self, position_x, position_y, direction, tag):
            super().__init__()
            self.tag = tag
            self.posicao_x = position_x
            self.posicao_y = position_y
            self.stopped = False
            self.direction = direction
            self.beacon_stop = False
            self.intersection = []

        async def move_and_send(self, direction, x_change, y_change):
            self.posicao_x += x_change
            self.posicao_y += y_change

            intersection_conditions = {
                "up": (self.posicao_y - 1 == self.intersection[2] and self.posicao_x - 1 == self.intersection[1]),
                "down": (self.posicao_y + 1 == self.intersection[2] and self.posicao_x + 1 == self.intersection[1]),
                "left": (self.posicao_y - 1 == self.intersection[2] and self.posicao_x + 1 == self.intersection[1]),
                "right": (self.posicao_y + 1 == self.intersection[2] and self.posicao_x - 1 == self.intersection[1]),
            }
            if self.beacon_stop:
                if direction in intersection_conditions and intersection_conditions[direction]:
                    self.beacon_stop = False
                    beacon_msg = Message(to=f"{self.intersection[3]}")
                    beacon_msg.set_metadata("performative", "agree")
                    beacon_msg.body = f"PASSED;{self.tag};{self.posicao_x};{self.posicao_y};{direction};{self.agent.jid}"
                    print("Sent beacon")
                    await self.send(beacon_msg)
                    self.intersection = []

        async def run(self):
            counter = 0

            while True:
                if not self.stopped:
                    counter += 1
                    await self.send_beacon(counter)
                    if counter == 2:
                        counter = 0

                    await self.handle_direction()

                    await self.check_traffic_light()
                    await asyncio.sleep(1)
                else:
                    print(f"Car stopped at position ({self.posicao_x}, {self.posicao_y})")
                    await self.check_traffic_light()

                    await asyncio.sleep(1)

        async def send_beacon(self, count):
            if not self.beacon_stop:
                if count == 2:
                    for intersection in intersections:
                        distance = math.sqrt((self.posicao_x - intersection.position_x) ** 2 +
                                             (self.posicao_y - intersection.position_y) ** 2)
                        if distance <= 5:
                            if (
                                    (self.direction == "up" and self.posicao_y < intersection.position_y) or
                                    (self.direction == "down" and self.posicao_y > intersection.position_y) or
                                    (self.direction == "left" and self.posicao_x > intersection.position_x) or
                                    (self.direction == "right" and self.posicao_x < intersection.position_x)
                            ):
                                beacon_msg = Message(to=f"{intersection.jid}")
                                beacon_msg.set_metadata("performative", "agree")
                                beacon_msg.body = f"BEACON;{self.tag};{self.posicao_x};{self.posicao_y};{self.direction};{self.agent.jid}"
                                print("Sent beacon")
                                await self.send(beacon_msg)

        async def handle_direction(self):
            directions = {
                "up": (self.move_and_send, 0, 1),
                "down": (self.move_and_send, 0, -1),
                "left": (self.move_and_send, -1, 0),
                "right": (self.move_and_send, 1, 0),
            }

            if self.direction in directions:
                action, x_change, y_change = directions[self.direction]
                await action(self.direction, x_change, y_change)

        async def check_traffic_light(self):
            response = await self.receive(timeout=1)
            if response:
                if response.body.startswith("RECEIVED"):
                    self.beacon_stop = True
                    parts = response.body.split(";")
                    self.intersection.extend(parts)

                if response.body.startswith("SEMAFORO"):
                    parts = response.body.split(";")
                    if len(parts) == 4:
                        semaforo_position_x = int(parts[2])
                        semaforo_position_y = int(parts[3])
                        if semaforo_position_x == self.posicao_x and semaforo_position_y == self.posicao_y:
                            self.stopped = parts[1] != "Verde"

            else:
                if not self.stopped:
                    print("Did not receive a message but moved anyway")
                    if not self.stopped:
                        if self.direction == "up":
                            self.posicao_y += 1
                        if self.direction == "down":
                            self.posicao_y -= 1
                        if self.direction == "left":
                            self.posicao_x -= 1
                        if self.direction == "right":
                            self.posicao_x += 1

                    print("Car at top right position ({}, {})".format(self.posicao_x, self.posicao_y))

        async def on_end(self):
            print("Behavior ended with exit code {}.".format(self.exit_code))

    def __init__(self, jid: str, password: str, position_x, position_y, direction, tag: str,
                 verify_security: bool = False):
        super().__init__(jid, password, verify_security)
        self.direction = direction
        self.behavior = None
        self.posicao_x = position_x
        self.posicao_y = position_y
        self.tag = tag

    async def setup(self):
        print("Agent starting at position ({}, {})...".format(self.posicao_x, self.posicao_y))
        self.behavior = self.CarBehavior(self.posicao_x, self.posicao_y, self.direction, self.tag)
        self.add_behaviour(self.behavior)
