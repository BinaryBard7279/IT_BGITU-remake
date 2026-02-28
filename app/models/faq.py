from sqlalchemy import Column, Integer, String, Text

from app.models import Base


class Faq(Base):
    __tablename__ = 'faqs'

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, index=True, nullable=False)
    answer = Column(Text, nullable=False)
