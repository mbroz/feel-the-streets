import enum
from sqlalchemy import Column, Boolean, Integer, ForeignKey, ForeignKeyConstraint, UnicodeText, Float
from ..sa_types import IntEnum
from sqlalchemy.orm import relationship
from . import Named
from .enums import OSMObjectType, InternetAccess

class ClubType(enum.Enum):
    yes = 1
    scuba_diving = 2
    music = 3
    board_games = 4
    

class Addressable(Named):
    __tablename__ = "addressables"
    __mapper_args__ = {'polymorphic_identity': 'addressable', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address")
    note = Column(UnicodeText)
    is_in = Column(UnicodeText)
    fixme = Column(UnicodeText)
    website = Column(UnicodeText)
    ele = Column(Float)
    club = Column(IntEnum(ClubType))
    description = Column(UnicodeText)
    level = Column(Integer)
    email = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    alt_name = Column(UnicodeText)
    loc_name = Column(UnicodeText)
    comment = Column(UnicodeText)
    opening_hours = Column(UnicodeText)
    disused_name = Column(UnicodeText)
    internet_access = Column(IntEnum(InternetAccess))

    def __str__(self):
        return super().__str__() + (", " + str(self.address) if self.address else "")
