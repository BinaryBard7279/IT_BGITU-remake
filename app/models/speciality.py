from sqlalchemy import Column, Integer, String, Text
from app.models import Base

class Speciality(Base):
    __tablename__ = 'specialities'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False, unique=True)
    qualification = Column(String, nullable=False)
    term = Column(Integer, nullable=False)
    direction = Column(String, nullable=False)
    description = Column(Text, nullable=False)
