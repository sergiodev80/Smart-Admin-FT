#!/bin/bash
set -e

echo "Esperando PostgreSQL..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done
echo "PostgreSQL listo"

echo "Ejecutando migraciones..."
python manage.py migrate --noinput

# Copiar archivos estáticos al volumen compartido
if [ -d "/app/staticfiles" ]; then
  echo "Copiando archivos estáticos al volumen..."
  mkdir -p /app/static
  cp -r /app/staticfiles/. /app/static/
fi

echo "Iniciando Gunicorn..."
exec "$@"
