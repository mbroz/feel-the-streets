from .generator import Generator
from shared.entities import Route

class RouteGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Route)
        self.renames("route", "type")
        self.renames("from", "from_")
        self.renames("lcn:description", "lcn_description")
        self.renames("public_transport:version", "public_transport_version")
        self.renames("note1", "note_1")
        self.renames("text_color", "text_colour")
        self.unprefixes("osmc")
        self.renames("osmonitor:road_components", "road_components")
        self.renames("note:cz", "note_cz")
    
    @staticmethod
    def accepts(props):
        return "route" in props or ("type" in props and props["type"] == "route")