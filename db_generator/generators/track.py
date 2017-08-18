from .road import RoadGenerator
from shared.models import Track

class TrackGenerator(RoadGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Track)
        self.renames("motorcar", "motorcar_allowed")
        self.renames("mtb:scale:uphill", "mtb_scale_uphill")
        self.renames("mtb:scale:uphill", "mtb_scale_uphill")
        self.renames("leisure", "type")
        self.removes("survey_date")
        self.removes("survey:date")
        
        
    def _prepare_properties(self, entity_spec, props, record):
        if "area" in props and props["area"] == "no": # Can someone explain the thinking behind this to me?
            del props["area"]
        return super()._prepare_properties(entity_spec, props, record)
    @staticmethod
    def accepts(props):
        return (RoadGenerator.accepts(props) and (props["highway"] == "track") or "leisure" in props and props["leisure"] == "track") or "tracktype" in props