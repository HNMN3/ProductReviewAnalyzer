from config import Base, engine
from database import Entity, Review

Base.metadata.create_all(engine)
