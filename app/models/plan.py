from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models import Base

class Track(Base):
    __tablename__ = 'tracks'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False, unique=True)
    
    directions = relationship("Direction", back_populates="track", cascade="all, delete-orphan")

class Direction(Base):
    __tablename__ = 'directions'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False, unique=True)
    track_id = Column(Integer, ForeignKey('tracks.id', ondelete='CASCADE'), nullable=False)
    
    track = relationship("Track", back_populates="directions")
    disciplines = relationship("Discipline", back_populates="direction", cascade="all, delete-orphan")

class Discipline(Base):
    __tablename__ = "disciplines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False, unique=True)
    start_term = Column(Integer, nullable=False)
    end_term = Column(Integer, nullable=False)
    direction_id = Column(Integer, ForeignKey('directions.id', ondelete='CASCADE'), nullable=False)
    
    direction = relationship("Direction", back_populates="disciplines")
