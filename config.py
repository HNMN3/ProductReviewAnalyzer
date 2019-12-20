import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

try:
    database_uri = os.environ['DATABASE_URI']
    engine = create_engine(database_uri)
    Session = sessionmaker(bind=engine)
    Base = declarative_base()
except:
    print("DATABASE_URI env variable not set aborting!!")
    quit()
