from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import os

import models
import schemas
import crud
from database import SessionLocal, engine

app = FastAPI()

# Configuração JWT
SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta-altere-em-producao")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 dias

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )
    return user

# Endpoints de Autenticação
@app.post("/cadastro", response_model=schemas.Token)
def cadastro(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    new_user = crud.create_user(db, user)
    access_token = create_access_token(data={"sub": new_user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }

@app.post("/login", response_model=schemas.Token)
def login(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, user_login.email, user_login.senha)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@app.get("/me", response_model=schemas.User)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# Endpoints de Grupo
@app.post("/grupos", response_model=schemas.GrupoComMembros)
def create_group(
    group: schemas.GrupoCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_group = crud.create_group(db, group, criado_por_id=current_user.id)
    member_ids = crud.get_group_member_ids(db, new_group.id)
    return {
        "id": new_group.id,
        "titulo": new_group.titulo,
        "criado_por_id": new_group.criado_por_id,
        "created_at": new_group.created_at,
        "membro_ids": member_ids,
    }


@app.get("/grupos", response_model=list[schemas.GrupoComMembros])
def list_my_groups(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    groups = crud.get_user_groups(db, current_user.id)
    result = []
    for group in groups:
        result.append(
            {
                "id": group.id,
                "titulo": group.titulo,
                "criado_por_id": group.criado_por_id,
                "created_at": group.created_at,
                "membro_ids": crud.get_group_member_ids(db, group.id),
            }
        )
    return result


@app.get("/grupos/{grupo_id}/items", response_model=list[schemas.Item])
def list_group_items(
    grupo_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not crud.is_user_in_group(db, grupo_id, current_user.id):
        raise HTTPException(status_code=403, detail="Acesso negado ao grupo")
    return crud.get_group_items(db, grupo_id)


@app.post("/grupos/{grupo_id}/items", response_model=schemas.Item)
def create_group_item(
    grupo_id: int,
    item: schemas.ItemCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not crud.is_user_in_group(db, grupo_id, current_user.id):
        raise HTTPException(status_code=403, detail="Acesso negado ao grupo")
    return crud.create_item(db, grupo_id, item, criado_por_id=current_user.id)


# Endpoints de Item
@app.get("/items/{item_id}", response_model=schemas.Item)
def get_item(
    item_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    if item.grupo_id is None or not crud.is_user_in_group(db, item.grupo_id, current_user.id):
        raise HTTPException(status_code=403, detail="Acesso negado ao item")
    return item

@app.put("/items/{item_id}", response_model=schemas.Item)
def update_item(
    item_id: int,
    item_update: schemas.ItemUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_item = crud.get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    if db_item.grupo_id is None or not crud.is_user_in_group(db, db_item.grupo_id, current_user.id):
        raise HTTPException(status_code=403, detail="Acesso negado ao item")

    item = crud.update_item(db, item_id, item_update)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item

@app.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_item = crud.get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    if db_item.grupo_id is None or not crud.is_user_in_group(db, db_item.grupo_id, current_user.id):
        raise HTTPException(status_code=403, detail="Acesso negado ao item")

    item = crud.delete_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return {"ok": True}

@app.get("/health")
def health():
    return {"status": "ok"}