import uuid
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from sqlalchemy.sql import func
import os

Base = declarative_base()

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String, unique=True)  # Store UUID as string
    user_id = Column(Integer)
    payload = Column(String)
    source = Column(String)
    destination_name = Column(String)
    retry_attempts = Column(Integer, default=0)
    processing_status = Column(Enum('Processing', 'Success', 'Failed'), default='Processing')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Event(event_id={self.event_id}, destination={self.destination_name}, processing_status={self.processing_status}, created_at={self.created_at})>"

# Create an SQLite database engine
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FILE_URL = BASE_DIR +  "/data/events.db"
DATABASE_URL = f'sqlite:///{FILE_URL}'

engine = create_engine(DATABASE_URL, echo=True)  # Set echo=True for debugging

# Create tables
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()
