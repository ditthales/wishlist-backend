#!/bin/bash
# Script para rodar migrations automaticamente no deploy

echo "Running database migrations..."
alembic upgrade head
echo "Migrations completed!"
