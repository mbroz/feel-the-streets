from .generator import Generator
from shared.entities import Stop

class StopGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Stop)
        self.renames("highway", "type")
        self.renames("amenity", "type")
        self.renames("railway", "type")
        self.renames("shelter", "has_shelter")
        self.renames("route:ref", "route_ref")
        self.renames("alt_name:de", "alt_name_de")
        self.renames("old_name:de", "old_name_de")
        self.renames("network:en", "network_en")
        self.renames("network:cs", "network_cs")
        self.renames("zona", "zone")
        self.renames("toilets:wheelchair", "wheelchair_toilets")
    @staticmethod
    def accepts(props):
        return ("public_transport" in props and props["public_transport"] in {"stop_position", "station", "stop_area"}) or ("highway" in props and props["highway"] == "bus_stop") or ("amenity" in props and props["amenity"] == "bus_station") or ("railway" in props and props["railway"] == "tram_stop")