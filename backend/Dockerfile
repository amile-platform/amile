FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn pydantic pydantic-settings \
    sqlalchemy asyncpg alembic python-jose passlib python-dotenv \
    structlog numpy scipy scikit-learn
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
