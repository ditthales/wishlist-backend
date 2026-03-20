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


# Operações de Grupo
def get_group(db: Session, group_id: int):
    return db.query(models.Grupo).filter(models.Grupo.id == group_id).first()


def get_group_member_ids(db: Session, group_id: int) -> list[int]:
    rows = (
        db.query(models.GrupoMembro.user_id)
        .filter(models.GrupoMembro.grupo_id == group_id)
        .all()
    )
    return [row[0] for row in rows]


def is_user_in_group(db: Session, group_id: int, user_id: int) -> bool:
    member = (
        db.query(models.GrupoMembro)
        .filter(
            models.GrupoMembro.grupo_id == group_id,
            models.GrupoMembro.user_id == user_id,
        )
        .first()
    )
    return member is not None


def create_group(db: Session, group: schemas.GrupoCreate, criado_por_id: int):
    db_group = models.Grupo(titulo=group.titulo, criado_por_id=criado_por_id)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)

    unique_member_ids = set(group.membro_ids)
    unique_member_ids.add(criado_por_id)

    if unique_member_ids:
        users = (
            db.query(models.User.id)
            .filter(models.User.id.in_(list(unique_member_ids)))
            .all()
        )
        existing_user_ids = {user_id for (user_id,) in users}

        memberships = [
            models.GrupoMembro(grupo_id=db_group.id, user_id=user_id)
            for user_id in existing_user_ids
        ]
        db.add_all(memberships)
        db.commit()

    return db_group


def get_user_groups(db: Session, user_id: int):
    return (
        db.query(models.Grupo)
        .join(models.GrupoMembro, models.GrupoMembro.grupo_id == models.Grupo.id)
        .filter(models.GrupoMembro.user_id == user_id)
        .order_by(models.Grupo.created_at.desc())
        .all()
    )

# Operações de Item
def create_item(db: Session, group_id: int, item: schemas.ItemCreate, criado_por_id: int):
    db_item = models.Item(
        nome=item.nome,
        link=item.link,
        grupo_id=group_id,
        para_quem_id=item.para_quem_id,
        criado_por_id=criado_por_id,
        comprado=False
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_group_items(db: Session, group_id: int):
    return (
        db.query(models.Item)
        .filter(models.Item.grupo_id == group_id)
        .order_by(models.Item.created_at.desc())
        .all()
    )

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