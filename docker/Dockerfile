# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev pkg-config gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt .
RUN pip install --user --no-cache-dir -r base.txt

# Stage 2: Final
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev netcat-openbsd gettext \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
# Set STATIC_ROOT for build-time collectstatic
ENV STATIC_ROOT=/app/staticfiles
COPY . .

RUN python manage.py compilemessages
RUN python manage.py collectstatic --noinput

EXPOSE 8000

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]
