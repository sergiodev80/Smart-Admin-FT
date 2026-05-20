# Smart AdminAI Template

Template base para proyectos de administración interna con Django + Unfold Admin + Docker.

## Stack

- **Django 6** + Python 3.12
- **Unfold Admin** — UI de administración moderna
- **PostgreSQL** — base de datos principal
- **Docker** — entorno de desarrollo containerizado
- **i18n** — soporte español / inglés

## Incluye de base

- User model personalizado con roles (admin, pm, translator, reviewer)
- Flujo de solicitud de acceso con activación por email
- Login con email o username
- Selector de idioma
- Makefile con shortcuts para todos los comandos frecuentes
- Configuración separada dev / producción
- Tests base para core

## Inicio rápido

```bash
# 1. Clonar
git clone https://github.com/sergiodev80/Smart-AdminAI-Template.git mi-proyecto
cd mi-proyecto

# 2. Configurar entorno
cp .env.example .env.dev
# Editar .env.dev con los valores del proyecto

# 3. Levantar
make up

# 4. Migraciones y superusuario
make migrate
make createsuperuser
```

El proyecto corre en [http://localhost:8001](http://localhost:8001)

## Personalización al usar el template

Ver sección "Al iniciar un proyecto desde este template" en `CLAUDE.md`.
