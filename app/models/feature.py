# app/models/feature.py
from sqlalchemy import Column, Integer, String, Text
from app.models import Base

class Feature(Base):
    __tablename__ = 'features'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    svg_code = Column(Text, nullable=True)