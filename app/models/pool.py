from sqlalchemy import Column, Integer, String, Boolean
from app.db.session import Base


class Pool(Base):
    __tablename__ = "pools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sequence_order = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
