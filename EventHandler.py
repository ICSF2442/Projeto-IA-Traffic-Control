class EventHandler:
    def __init__(self):
        self.listeners = {}

    def add_listener(self, event, callback):
        if event not in self.listeners:
            self.listeners[event] = callback

    def trigger_event(self, event, info):
        if event in self.listeners:
            self.listeners[event](info)
