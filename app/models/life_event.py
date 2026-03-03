from sqlalchemy import Boolean, Column, Integer, String

from app.models import Base


class LifeEvent(Base):
    __tablename__ = "life_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    tag = Column(String, nullable=False)  # Тема (например: "Событие", "Команда")
    image_url = Column(String, nullable=False)
    is_main = Column(Boolean, default=False)  # Если True — попадает в Bento Grid
    order = Column(Integer, default=0)
