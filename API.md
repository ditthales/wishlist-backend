# Wishlist Backend – Documentação de Endpoints

Data: 26/03/2026

## Visão geral
- Base URL: defina no seu app (ex.: `http://localhost:8000`)
- Autenticação: Bearer Token (JWT)
- Header padrão:
  - `Authorization: Bearer <access_token>`
  - `Content-Type: application/json`

## Autenticação
### POST /cadastro
Cria um usuário e retorna token.

**Body**
```json
{
  "nome": "Fulano",
  "email": "fulano@email.com",
  "foto": "https://...",
  "senha": "minha_senha"
}
```

**Resposta 200**
```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "nome": "Fulano",
    "email": "fulano@email.com",
    "foto": "https://...",
    "created_at": "2026-03-26T12:00:00"
  }
}
```

**Erros**
- 400: Email já cadastrado

---

### POST /login
Autentica usuário e retorna token.

**Body**
```json
{
  "email": "fulano@email.com",
  "senha": "minha_senha"
}
```

**Resposta 200**
```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "nome": "Fulano",
    "email": "fulano@email.com",
    "foto": "https://...",
    "created_at": "2026-03-26T12:00:00"
  }
}
```

**Erros**
- 401: Email ou senha incorretos

---

### GET /me
Retorna o usuário autenticado.

**Auth**: Bearer

**Resposta 200**
```json
{
  "id": 1,
  "nome": "Fulano",
  "email": "fulano@email.com",
  "foto": "https://...",
  "created_at": "2026-03-26T12:00:00"
}
```

**Erros**
- 401: Token inválido
- 401: Usuário não encontrado

---

## Grupos
### POST /grupos
Cria um grupo e retorna o grupo com membros.

**Auth**: Bearer

**Body**
```json
{
  "titulo": "Amigo Secreto",
  "membro_ids": [2, 3]
}
```

**Resposta 200**
```json
{
  "id": 10,
  "titulo": "Amigo Secreto",
  "criado_por_id": 1,
  "created_at": "2026-03-26T12:00:00",
  "membro_ids": [1, 2, 3]
}
```

---

### GET /grupos
Lista grupos do usuário autenticado (com membros).

**Auth**: Bearer

**Resposta 200**
```json
[
  {
    "id": 10,
    "titulo": "Amigo Secreto",
    "criado_por_id": 1,
    "created_at": "2026-03-26T12:00:00",
    "membro_ids": [1, 2, 3]
  }
]
```

---

### GET /grupos/{grupo_id}/items
Lista itens de um grupo.

**Auth**: Bearer

**Parâmetros**
- `grupo_id` (int)

**Resposta 200**
```json
[
  {
    "id": 100,
    "nome": "Fone de ouvido",
    "link": "https://...",
    "para_quem_id": 2,
    "grupo_id": 10,
    "criado_por_id": 1,
    "comprado": false,
    "created_at": "2026-03-26T12:00:00"
  }
]
```

**Erros**
- 403: Acesso negado ao grupo

---

### POST /grupos/{grupo_id}/items
Cria item em um grupo.

**Auth**: Bearer

**Parâmetros**
- `grupo_id` (int)

**Body**
```json
{
  "nome": "Fone de ouvido",
  "link": "https://...",
  "para_quem_id": 2
}
```

**Resposta 200**
```json
{
  "id": 100,
  "nome": "Fone de ouvido",
  "link": "https://...",
  "para_quem_id": 2,
  "grupo_id": 10,
  "criado_por_id": 1,
  "comprado": false,
  "created_at": "2026-03-26T12:00:00"
}
```

**Erros**
- 403: Acesso negado ao grupo

---

## Itens
### GET /items/{item_id}
Retorna um item.

**Auth**: Bearer

**Parâmetros**
- `item_id` (int)

**Resposta 200**
```json
{
  "id": 100,
  "nome": "Fone de ouvido",
  "link": "https://...",
  "para_quem_id": 2,
  "grupo_id": 10,
  "criado_por_id": 1,
  "comprado": false,
  "created_at": "2026-03-26T12:00:00"
}
```

**Erros**
- 403: Acesso negado ao item
- 404: Item não encontrado

---

### PUT /items/{item_id}
Atualiza um item.

**Auth**: Bearer

**Parâmetros**
- `item_id` (int)

**Body** (campos opcionais)
```json
{
  "nome": "Novo nome",
  "link": "https://...",
  "comprado": true
}
```

**Resposta 200**
```json
{
  "id": 100,
  "nome": "Novo nome",
  "link": "https://...",
  "para_quem_id": 2,
  "grupo_id": 10,
  "criado_por_id": 1,
  "comprado": true,
  "created_at": "2026-03-26T12:00:00"
}
```

**Erros**
- 403: Acesso negado ao item
- 404: Item não encontrado

---

### DELETE /items/{item_id}
Remove um item.

**Auth**: Bearer

**Parâmetros**
- `item_id` (int)

**Resposta 200**
```json
{
  "ok": true
}
```

**Erros**
- 403: Acesso negado ao item
- 404: Item não encontrado

---

## Saúde
### GET /health
Verificação de status.

**Resposta 200**
```json
{
  "status": "ok"
}
```
