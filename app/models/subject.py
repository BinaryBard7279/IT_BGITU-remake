# app/models/subject.py
from sqlalchemy import Column, Integer, String, Text
from app.models import Base

class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False, unique=True)
    description = Column(String, nullable=False)
    svg_code = Column(Text, nullable=True) # Поле в базе данных