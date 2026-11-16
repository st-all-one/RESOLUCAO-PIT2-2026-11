# syntax=docker/dockerfile:1

# ---------------------------------------------------------------- front-end
FROM node:22-alpine AS frontend

WORKDIR /app
COPY package.json package-lock.json tsconfig.json ./
COPY frontend ./frontend
RUN npm ci --ignore-scripts && npm run build

# ------------------------------------------------------------------ runtime
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY --from=frontend /app/src/app/static/js ./src/app/static/js
RUN pip install .

COPY db ./db

RUN useradd --create-home --uid 10001 app
USER app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
