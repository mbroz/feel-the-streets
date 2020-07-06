import attr
from . import entity_pre_move, entity_post_move, entity_pre_enter, entity_post_enter, entity_pre_leave, entity_post_leave, entity_rotated, entity_move_rejected
from ..measuring import measure
from pygeodesy.ellipsoidalVincenty import LatLon

@attr.s
class Entity:
    use_step_sounds = False
    map = attr.ib(hash=False)
    position = attr.ib(hash=False)
    is_inside_of = attr.ib(default=attr.Factory(set), hash=False)
    direction = attr.ib(default=0, hash=False)

    def move_to(self, pos):
        if entity_pre_move.has_receivers_for(self):
            for func, ret in entity_pre_move.send(self, new_pos=pos):
                if not ret:
                    entity_move_rejected.send(self)
                    return False
        with measure("Inside of query"):
            new_inside_of = set(entity for entity in self.map.intersections_at_position(pos))
        if entity_pre_enter.has_receivers_for(self) or entity_post_enter.has_receivers_for(self):
            enters = new_inside_of.difference(self.is_inside_of)
        if entity_pre_enter.has_receivers_for(self):
            for entered in enters:
                for func, ret in entity_pre_enter.send(self, enters=entered):
                    if not ret:
                        entity_move_rejected.send(self)
                        return False
        if entity_pre_leave.has_receivers_for(self) or entity_post_leave.has_receivers_for(self):
            leaves = self.is_inside_of.difference(new_inside_of)
        if entity_pre_leave.has_receivers_for(self):
            for leaving in leaves:
                for func, ret in entity_pre_leave.send(self, leaves=leaving):
                    if not ret:
                        entity_move_rejected.send(self)
                        return False
        # Keeping more than 7 decimal digits is pointless as we can not get anything more accurate from OSM anyway.
        rounded_pos = pos.latlon2(7)
        self.position = LatLon(rounded_pos.lat, rounded_pos.lon)
        self.is_inside_of = new_inside_of
        if entity_post_leave.has_receivers_for(self):
            for place in leaves:
                entity_post_leave.send(self, leaves=place)
        if entity_post_leave.has_receivers_for(self):
            for place in enters:
                entity_post_enter.send(self, enters=place)
        entity_post_move.send(self)
    
    def move_by(self, pos_delta):
        pos, new_dir = self.position.destination2(pos_delta, self.direction)
        self.move_to(pos)
        self.direction = new_dir
    
    def rotate(self, amount):
        self.set_direction((self.direction + amount) % 360)
    
    def set_direction(self, direction):
        self.direction = direction
        entity_rotated.send(self)
    
    @property
    def cartesian_position(self):
        cartesian = self.position.toCartesian()
        return cartesian.x, cartesian.y, cartesian.z
