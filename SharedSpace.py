

class SharedSpace:
    def __init__(self):
        self.space = {}  # Dictionary to represent the shared space

    def is_position_occupied(self, x, y):
        return (x, y) in self.space

    def occupy_position(self, x, y, tag):
        self.space[(x, y)] = tag

    def free_position(self, x, y):
        if (x, y) in self.space:
            del self.space[(x, y)]
