#!/bin/bash
# Script de inicialização para o Render

# Rodar migrations
echo "Running database migrations..."
alembic upgrade head

# Iniciar servidor
echo "Starting server..."
uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
