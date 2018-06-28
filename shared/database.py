import glob
import os
import logging
import json
import sqlite3
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from shapely import wkt
from geoalchemy import GeometryDDL, WKTSpatialElement
import appdirs
from .models import Entity, IdxEntitiesGeometry
from .time_utils import ts_to_utc
from .diff_utils import apply_dict_change
from .semantic_change import ChangeType

log = logging.getLogger(__name__)

class Database:
    
    @classmethod
    def get_database_storage_root(cls, server_side=True):
        if server_side:
            root = os.path.abspath("areas")
        else:
            root = os.path.join(appdirs.user_data_dir("fts", appauthor=False), "areas")
        if not os.path.exists(root):
            os.makedirs(root)
        return root
    
    @classmethod
    def get_database_file(cls, area_name, server_side=True, name_suffix=""):
        return os.path.join(cls.get_database_storage_root(server_side), "%s%s.db"%(area_name, name_suffix))
    
    @classmethod
    def get_local_databases_info(cls, server_side=True):
        entries = []
        for fname in glob.glob(os.path.join(cls.get_database_storage_root(server_side), "*.db")):
            info = os.stat(fname)
            entries.append(dict(name=os.path.basename(fname).replace(".db", ""), state="local", created_at=ts_to_utc(info.st_ctime), updated_at=ts_to_utc(info.st_mtime)))
        return entries

    def __init__(self, area_name, server_side=True, name_suffix=""):
        self._area_name = area_name
        db_path = self.get_database_file(area_name, server_side, name_suffix)
        self._creating = False
        self._engine = create_engine("sqlite:///%s"%db_path)
        event.listen(self._engine, "connect", self._post_connect)
        self._session = sessionmaker(bind=self._engine)()
        self._entity_insert_statement = None
        
    def _post_connect(self, dbapi_connection, connection_record):
        dbapi_connection.enable_load_extension(True)
        if os.name == "nt":
            extension = "dll"
        elif os.name == "posix":
            extension = "so"
        else:
            raise RuntimeError("Operating system %s not tested, sqlite3 extension loading specifics not known."%os.name)
        dbapi_connection.load_extension("mod_spatialite.%s"%extension)
        try:
            dbapi_connection.load_extension("icu.%s"%extension)
        except sqlite3.OperationalError:
            log.warning("Failed to load the icu extension, the  text searches will be case sensitive.")
        if self._creating: 
            log.debug("Initializing spatial metadata...")
            dbapi_connection.execute("SELECT InitSpatialMetadata(1)")

    def create_if_needed(self):
        self._creating = not self._engine.dialect.has_table(self._engine, "entities")
        if self._creating:
            log.debug("Running geometry DDL...")
            GeometryDDL(Entity.__table__)
            log.debug("Creating database tables...")
            Entity.__table__.create(self._engine)
            self._creating = False

    def add(self, instance):
        self._session.add(instance)

    def commit(self):
        self._session.commit()
    
    def merge(self, entity):
        self._session.merge(entity)
    
    def query(self, *entities, **kwargs):
        return self._session.query(*entities, **kwargs)

    def scalar(self, *args, **kwargs):
        return self._session.scalar(*args, **kwargs)

    @property
    def bounds(self):
        min = func.min
        max = func.max
        return self._session.query(min(IdxEntitiesGeometry.xmin), max(IdxEntitiesGeometry.xmax), min(IdxEntitiesGeometry.ymin), max(IdxEntitiesGeometry.ymax)).one()

    @property
    def last_timestamp(self):
        max = func.max
        json_extract = func.json_extract
        return self.scalar(max(json_extract(Entity.data, "$.timestamp")))
    
    def prepare_entity_insertions(self):
        self._session.execute("pragma synchronous=off")
        self._entity_insert_statement = Entity.__table__.insert().values(dict(id=":id", data=":data", discriminator=":discriminator", effective_width=":effective_width", geometry=text("GeomFromText(:geometry, 4326)")))

    def insert_entity(self, entity):
        self._session.execute(self._entity_insert_statement, dict(id=entity.id, discriminator=entity.discriminator, data=entity.data, effective_width=entity.effective_width, geometry=entity.geometry.desc))

    def commit_entity_insertions(self):
        self._session.commit()

   
    def has_entity(self, osm_id):
        return self.query(Entity).filter(func.json_extract(Entity.data, text('"$.osm_id"')) == osm_id).count() > 0

    def get_entity_by_osm_id(self, osm_id):
        # The text construct is necessary, because sqlite will not use a functional index if one of the function's arguments is supplied through a placeholder.
        query = self.query(Entity).filter(func.json_extract(Entity.data, text('"$.osm_id"')) == osm_id)
        try:
            return query[-1]
        except IndexError:
            return None

    def apply_change(self, change):
        entity = None
        if change.type is ChangeType.create:
            entity = Entity()
            self.add(entity)
        elif change.type in {ChangeType.update, ChangeType.delete}:
            entity = self.get_entity_by_osm_id(change.osm_id)
            if not entity:
                log.warning("Entity with osm id %s not found in the local database.", change.osm_id)
                return
        if change.type is ChangeType.delete:
            self._session.delete(entity)
        else:
            old_geom = entity.geometry
            for subchange in change.property_changes:
                apply_dict_change(subchange, entity.__dict__)
            if isinstance(entity.geometry, str):
                geom_valid = False
                try:
                    geom_valid = wkt.loads(entity.geometry).is_valid
                except Exception:
                    pass
                if not geom_valid:
                    log.warning("Refusing to set geometry of object %s to %s.", entity.data, entity.geometry)
                    entity.geometry = old_geom
                else:
                    entity.geometry = WKTSpatialElement(entity.geometry)
            if change.data_changes:
                entity_data = json.loads(entity.data)
                for subchange in change.data_changes:
                    entity_data = apply_dict_change(subchange, entity_data)
                entity.data = json.dumps(entity_data)
        return entity

    def close(self):
        self._session.close()
    def rollback(self):
        self._session.rollback()