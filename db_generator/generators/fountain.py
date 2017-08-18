from .generator import Generator
from shared.models import Fountain

class FountainGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Fountain)
        self.removes("amenity")

    @staticmethod
    def accepts(props):
        return "amenity" in props and props["amenity"] == "fountain"