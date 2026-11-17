# syntax=docker/dockerfile:1

# ---------------------------------------------------------------- front-end
FROM node:22-alpine AS frontend

WORKDIR /app
COPY frontend ./frontend
COPY backend/app/static ./backend/app/static
RUN cd frontend && npm ci --ignore-scripts && npm run build

# ------------------------------------------------------------------ runtime
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY backend ./backend
COPY --from=frontend /app/backend/app/static/js ./backend/app/static/js
COPY --from=frontend /app/backend/app/static/css ./backend/app/static/css
RUN pip install .

COPY database ./database

RUN useradd --create-home --uid 10001 app \
    && mkdir -p /app/uploads \
    && chown -R app:app /app/uploads
USER app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
