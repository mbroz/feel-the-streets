from .address_aware import AddressAwareGenerator
from shared.entities import Leisure

class LeisureGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Leisure)
        self.renames("leisure", "type")
        self.renames("dog", "dogs_allowed")
        self.renames("athletics:shot-put", "shot_put")
        self.unprefixes("contact")
        self.unprefixes("athletics")

        self.renames("boats:small", "small_boats")
    def _prepare_properties(self, entity_spec, props, record):
        if "sport" in props:
            props["sport"] = props["sport"].replace("9", "nine_")
        return super()._prepare_properties(entity_spec, props, record)

    @staticmethod
    def accepts(props):
        return "leisure" in props