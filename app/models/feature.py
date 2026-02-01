from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models import Base

class Feature(Base):
    __tablename__ = 'features'

    id = Column(Integer, primary_key=True, index=True)
    speciality_id = Column(Integer, ForeignKey('specialities.id', ondelete='CASCADE'), nullable=False)
    subtitle = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    
    speciality = relationship("Speciality", back_populates="features")
