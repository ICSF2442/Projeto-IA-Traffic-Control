import time


# Classe que irá guardar e calcular tempos de espera dos carros quando estes esperam pelo semaforo

class WaitingTimeManager:
    def __init__(self):
        self.stopped_times = {
            "north": None,
            "south": None,
            "east": None,
            "west": None
        }

        self.direction_mapping = {
            "up": "south",
            "down": "north",
            "left": "east",
            "right": "west"
        }

    def car_stopped(self, direction):
        stopped_time = time.time()
        self.stopped_times[
            self.direction_mapping.get(direction)] = stopped_time  # Record stopped time based on direction mapping

    def car_continued(self, direction):
        self.stopped_times[
            self.direction_mapping.get(direction)] = None  # Reset the stopped time when the car continues

    def get_time_for_direction(self, direction):
        stopped_time = self.stopped_times[direction]
        if stopped_time is not None:
            return int(time.time() - stopped_time)
        return 0  # Return 0 if the car is not currently stopped
