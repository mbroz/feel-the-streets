from .generator import Generator
from shared.models import FireHydrant

class FireHydrantGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(FireHydrant)
        self.removes("emergency")
        self.renames("fire_hydrant:type", "type")

    @staticmethod
    def accepts(props):
        return "fire_hydrant:type" in props or ("emergency" in props and props["emergency"] == "fire_hydrant")