from sqlalchemy import Column, Integer, String, Text
from app.models import Base

class TimelineStep(Base):
    __tablename__ = 'timeline_steps'

    id = Column(Integer, primary_key=True, index=True)
    order = Column(Integer, default=0, nullable=False)
    term = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    color_class = Column(String, nullable=False, default="bg-pastel-sky")
