from sqlalchemy import Column, Integer, String, ForeignKey, Text
from app.models import Base

class Achievement(Base):
    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True, index=True)
    theme = Column(String, index=True, nullable=False)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
