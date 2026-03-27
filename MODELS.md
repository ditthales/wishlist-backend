# Wishlist Backend – Modelos de Dados

Data: 26/03/2026

Este documento descreve os modelos persistidos no banco e como se relacionam, para você espelhar no app (Flutter).

## Visão geral de relacionamentos
- `User` 1:N `Grupo` (um usuário cria vários grupos via `criado_por_id`)
- `User` N:N `Grupo` (membros do grupo via tabela `GrupoMembro`)
- `Grupo` 1:N `Item` (itens pertencem a um grupo)
- `User` 1:N `Item` (quem cria via `criado_por_id`)
- `User` 1:N `Item` (para quem é o item via `para_quem_id`)


## User
Tabela: `users`

**Campos**
- `id` (int, PK)
- `nome` (string, obrigatório)
- `email` (string, único, obrigatório)
- `senha_hash` (string, obrigatório) — não deve ser exposto no app
- `foto` (string, opcional)
- `created_at` (datetime)

**Observações**
- No app, você usa o modelo público de usuário (sem `senha_hash`).
- `email` é único e serve para autenticação.

**Modelo recomendado no app (público)**
- `id: int`
- `nome: String`
- `email: String`
- `foto: String?`
- `createdAt: DateTime`


## Grupo
Tabela: `grupos`

**Campos**
- `id` (int, PK)
- `titulo` (string, obrigatório)
- `criado_por_id` (int, FK → `users.id`)
- `created_at` (datetime)

**Relacionamentos**
- Criador do grupo: `criado_por_id`
- Membros: tabela de junção `GrupoMembro`

**Modelo recomendado no app**
- `id: int`
- `titulo: String`
- `criadoPorId: int`
- `createdAt: DateTime`
- `membroIds: List<int>` (vem no endpoint de grupos)


## GrupoMembro
Tabela: `grupo_membros`

**Campos**
- `grupo_id` (int, PK/FK → `grupos.id`)
- `user_id` (int, PK/FK → `users.id`)
- `created_at` (datetime)

**Finalidade**
- Representa a relação N:N entre `User` e `Grupo`.
- No app, normalmente você não precisa de um modelo explícito, apenas a lista de `membroIds` no `Grupo`.


## Item
Tabela: `items`

**Campos**
- `id` (int, PK)
- `nome` (string, obrigatório)
- `link` (string, opcional)
- `grupo_id` (int, FK → `grupos.id`, opcional)
- `para_quem_id` (int, FK → `users.id`, obrigatório)
- `criado_por_id` (int, FK → `users.id`, obrigatório)
- `comprado` (bool, default false)
- `created_at` (datetime)

**Observações**
- `grupo_id` pode ser nulo (mas nos endpoints atuais, itens estão vinculados a grupos).
- `para_quem_id` identifica o usuário que vai receber o item.
- `criado_por_id` identifica quem cadastrou o item.

**Modelo recomendado no app**
- `id: int`
- `nome: String`
- `link: String?`
- `grupoId: int?`
- `paraQuemId: int`
- `criadoPorId: int`
- `comprado: bool`
- `createdAt: DateTime`


## Modelos de API (DTOs) usados nos endpoints
Se quiser espelhar também os payloads de request/response:

### User (response)
- `id`, `nome`, `email`, `foto`, `created_at`

### UserCreate (request)
- `nome`, `email`, `foto`, `senha`

### UserLogin (request)
- `email`, `senha`

### GrupoCreate (request)
- `titulo`, `membro_ids` (lista de ids)

### GrupoComMembros (response)
- `id`, `titulo`, `criado_por_id`, `created_at`, `membro_ids`

### ItemCreate (request)
- `nome`, `link`, `para_quem_id`

### ItemUpdate (request)
- `nome?`, `link?`, `comprado?`

### Item (response)
- `id`, `nome`, `link`, `para_quem_id`, `grupo_id`, `criado_por_id`, `comprado`, `created_at`


## Dicas para o Flutter
- Use `DateTime.parse()` para campos `created_at`.
- Mapeie snake_case → camelCase no app.
- Nunca armazene `senha` ou `senha_hash` localmente.
