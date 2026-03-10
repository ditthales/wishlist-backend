from pydantic import BaseModel, EmailStr
from datetime import datetime

# Schemas de Item
class ItemBase(BaseModel):
    nome: str
    link: str | None = None
    para_quem_id: int

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    nome: str | None = None
    link: str | None = None
    comprado: bool | None = None

class Item(ItemBase):
    id: int
    criado_por_id: int
    comprado: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Schemas de Usuário
class UserBase(BaseModel):
    nome: str
    email: EmailStr
    foto: str | None = None

class UserCreate(UserBase):
    senha: str

class UserLogin(BaseModel):
    email: EmailStr
    senha: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User