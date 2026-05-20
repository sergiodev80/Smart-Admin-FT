#!/bin/bash
set -e

echo "Esperando PostgreSQL (dev)..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done
echo "PostgreSQL listo"

echo "Ejecutando migraciones..."
python manage.py migrate --noinput

echo "Iniciando servidor de desarrollo..."
exec "$@"
