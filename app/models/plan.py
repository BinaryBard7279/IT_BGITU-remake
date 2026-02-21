# app/models/plan.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models import Base

class Direction(Base):
    __tablename__ = 'directions'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False, unique=True)

    disciplines = relationship("Discipline", back_populates="direction", cascade="all, delete-orphan")

    def __str__(self):
        return self.name

class Discipline(Base):
    __tablename__ = "disciplines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    start_term = Column(Integer, nullable=False)
    end_term = Column(Integer, nullable=False)
    group = Column(String, nullable=False, server_default='Общие')
    direction_id = Column(Integer, ForeignKey('directions.id', ondelete='CASCADE'), nullable=False)

    direction = relationship("Direction", back_populates="disciplines")

    def __str__(self):
        return f"{self.name} ({self.group})"