from sqlalchemy import ARRAY, Column, Integer, String

from app.models import Base


class Teacher(Base):
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, unique=True, nullable=False)
    fio = Column(String, unique=True, index=True, nullable=False)
    post = Column(String, nullable=False)
    subjects = Column(ARRAY(String(100)), nullable=False, default=[])
