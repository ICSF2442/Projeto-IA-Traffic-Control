import asyncio
import math

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message


class AgentCar(Agent):
    class CarBehavior(CyclicBehaviour):
        def __init__(self, position_x, position_y, direction, tag, shared_space, intersections, waiting_time_manager,
                     event_handler):
            super().__init__()
            self.tag = tag
            self.posicao_x = position_x
            self.posicao_y = position_y
            self.stopped = False
            self.direction = direction
            self.beacon_stop = False
            self.intersection = []
            self.movement_occurred = False
            self.shared_space = shared_space
            self.intersections = intersections
            self.waiting_time_manager = waiting_time_manager
            self.XtoStop = None
            self.YtoStop = None
            self.traffic_color = None
            self.already_stopped_once = False
            self.event_handler = event_handler
            self.passei = False

        async def move_and_send(self, direction, x_change, y_change):
            self.posicao_x += x_change
            self.posicao_y += y_change
            self.event_handler.trigger_event(0, self.tag)

            if len(self.intersection) > 0:
                intersection_conditions = {
                    "up": (self.posicao_y - 1 > int(self.intersection[2])+1 and self.posicao_x - 1 == int(
                        self.intersection[1])),
                    "down": (self.posicao_y + 1 < int(self.intersection[2])+1 and self.posicao_x + 1 == int(
                        self.intersection[1])),
                    "left": (self.posicao_y - 1 == int(self.intersection[2]) and self.posicao_x + 1 <= int(
                        self.intersection[1])+1),
                    "right": (self.posicao_y + 1 == int(self.intersection[2]) and self.posicao_x - 1 >= int(
                        self.intersection[1])+1)
                }
                if self.beacon_stop:
                    if direction in intersection_conditions and intersection_conditions[direction]:
                        self.beacon_stop = False
                        beacon_msg = Message(to=f"{self.intersection[3]}")
                        beacon_msg.set_metadata("performative", "agree")
                        beacon_msg.body = f"PASSED;{self.tag};{self.posicao_x};{self.posicao_y};{direction};{self.agent.jid}"
                        print(f"Sent passed {self.tag}")
                        await self.send(beacon_msg)
                        self.passei = True
                        self.waiting_time_manager.car_continued(self.direction)
                        self.intersection = []
                        self.traffic_color = None
                        self.beacon_stop = False

        async def run(self):

            while True:
                if not self.stopped:
                    print(f"Car[{self.tag}] Coords:({self.posicao_x},{self.posicao_y})")
                    if not (
                            self.posicao_x == self.XtoStop and self.posicao_y == self.YtoStop and self.traffic_color == "Vermelho"):
                        await self.send_beacon()
                        await self.handle_direction()
                        await self.check_traffic_light()
                        self.movement_occurred = False
                    else:
                        self.stopped = True
                else:
                    print(f"Car [{self.tag}] stopped at position ({self.posicao_x}, {self.posicao_y})")
                    await self.check_traffic_light()

                await asyncio.sleep(1)

        async def send_beacon(self):
            if not self.beacon_stop:
                for intersection in self.intersections.get_intersections():
                    distance = math.sqrt((self.posicao_x - intersection.positionX) ** 2 +
                                         (self.posicao_y - intersection.positionY) ** 2)
                    if distance <= 6:
                        if (
                                (self.direction == "up" and self.posicao_y < intersection.positionY) or
                                (self.direction == "down" and self.posicao_y > intersection.positionY) or
                                (self.direction == "left" and self.posicao_x > intersection.positionX) or
                                (self.direction == "right" and self.posicao_x < intersection.positionX)
                        ):
                            beacon_msg = Message(to=f"{intersection.jid}")
                            beacon_msg.set_metadata("performative", "agree")
                            beacon_msg.body = f"BEACON;{self.tag};{self.posicao_x};{self.posicao_y};{self.direction};{self.agent.jid}"
                            print(f"Sent beacon {self.tag}")
                            await self.send(beacon_msg)

        async def handle_direction(self):
            directions = {
                "up": (self.move_and_send, 0, 1),
                "down": (self.move_and_send, 0, -1),
                "left": (self.move_and_send, -1, 0),
                "right": (self.move_and_send, 1, 0),
            }

            if self.direction in directions and not self.movement_occurred:
                action, x_change, y_change = directions[self.direction]
                next_x = self.posicao_x + x_change
                next_y = self.posicao_y + y_change
                past_x = self.posicao_x - x_change
                past_y = self.posicao_y - y_change

                if not self.shared_space.is_position_occupied(next_x, next_y):
                    await action(self.direction, x_change, y_change)
                    self.shared_space.free_position(past_x, past_y, self.tag)
                    self.shared_space.occupy_position(next_x, next_y, self.tag)
                    self.movement_occurred = True
                else:
                    # Wait until the next position is available
                    self.movement_occurred = True
                    print(f"{self.tag} Position ({next_x}, {next_y}) is occupied. Waiting...")

        async def check_traffic_light(self):
            response = await self.receive(timeout=3)
            if response:
                if response.body.startswith("RECEIVED"):
                    self.beacon_stop = True
                    parts = response.body.split(";")
                    self.intersection.extend(parts)

                if response.body.startswith("SEMAFORO"):
                    parts = response.body.split(";")
                    if len(parts) == 4:
                        self.traffic_color = parts[1]
                        semaforo_position_x = int(parts[2])
                        semaforo_position_y = int(parts[3])
                        self.XtoStop = semaforo_position_x
                        self.YtoStop = semaforo_position_y
                        if ((semaforo_position_x == self.posicao_x and semaforo_position_y == self.posicao_y) or
                                (self.XtoStop == self.posicao_x and self.YtoStop == self.posicao_y)):
                            if parts[1] != "Verde":
                                self.stopped = True
                                if not self.already_stopped_once:
                                    self.waiting_time_manager.car_stopped(self.direction)
                                    self.already_stopped_once = True
                            else:
                                self.stopped = False
            else:
                if not self.stopped and not self.movement_occurred:
                    await self.handle_direction()
                    print(f"carro{self.tag} moveu se:{self.posicao_x},{self.posicao_y}")

    def __init__(self, jid: str, password: str, position_x, position_y, direction, tag: str, shared_space,
                 event_handler,
                 waiting_time_manager,
                 intersections,
                 verify_security: bool = False):
        super().__init__(jid, password, verify_security)
        self.direction = direction
        self.behavior = None
        self.posicao_x = position_x
        self.posicao_y = position_y
        self.tag = tag
        self.shared_space = shared_space
        self.intersections = intersections
        self.waiting_time_manager = waiting_time_manager
        self.event_handler = event_handler

    async def setup(self):
        print("Agent starting at position ({}, {})...".format(self.posicao_x, self.posicao_y))
        self.behavior = self.CarBehavior(self.posicao_x, self.posicao_y, self.direction, self.tag, self.shared_space,
                                         self.intersections, self.waiting_time_manager, self.event_handler)
        self.add_behaviour(self.behavior)
