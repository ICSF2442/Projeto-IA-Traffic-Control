# Classe que armaneza todas as interseções
class Intersections:
    def __init__(self):
        self.intersection_array = []

    def add_intersection(self, intersection):
        self.intersection_array.append(intersection)

    def get_intersections(self):
        return self.intersection_array
