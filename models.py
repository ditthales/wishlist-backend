from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    senha_hash = Column(String, nullable=False)
    foto = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    link = Column(String, nullable=True)
    para_quem_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    criado_por_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comprado = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now())