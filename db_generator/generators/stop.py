from .generator import Generator
from shared.models import Stop

class StopGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Stop)
        self.removes("public_transport")
        self.removes("source_ref")
        self.renames("highway", "type")
        self.renames("amenity", "type")
        self.renames("railway", "type")
        self.renames("shelter", "has_shelter")
        self.removes("railway", True)
    @staticmethod
    def accepts(props):
        return ("public_transport" in props and props["public_transport"] in {"stop_position", "station"}) or ("highway" in props and props["highway"] == "bus_stop") or ("amenity" in props and props["amenity"] == "bus_station") or ("railway" in props and props["railway"] == "tram_stop")