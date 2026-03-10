from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models
import schemas

# Configuração para hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Operações de Usuário
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    senha_hash = hash_password(user.senha)
    db_user = models.User(
        nome=user.nome,
        email=user.email,
        senha_hash=senha_hash,
        foto=user.foto
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, senha: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(senha, user.senha_hash):
        return None
    return user

# Operações de Item
def create_item(db: Session, item: schemas.ItemCreate, criado_por_id: int):
    db_item = models.Item(
        nome=item.nome,
        link=item.link,
        para_quem_id=item.para_quem_id,
        criado_por_id=criado_por_id,
        comprado=False
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_items(db: Session, user_id: int | None = None):
    query = db.query(models.Item)
    if user_id:
        query = query.filter(models.Item.para_quem_id == user_id)
    return query.all()

def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def update_item(db: Session, item_id: int, item_update: schemas.ItemUpdate):
    db_item = get_item(db, item_id)
    if not db_item:
        return None
    
    update_data = item_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int):
    item = get_item(db, item_id)
    if item:
        db.delete(item)
        db.commit()
    return item