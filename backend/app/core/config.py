"""Application configuration using Pydantic Settings"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AMILE"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-replace-in-production"
    API_V1_STR: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://amile:password@localhost:5432/amile_db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_STUDENT_EVENTS: str = "student-interactions"

    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"

    # AI/ML Model Paths
    DKT_MODEL_PATH: str = "ml/models/dkt/saved_model"
    BKT_MODEL_PATH: str = "ml/models/bkt/saved_model"
    LLM_MODEL_NAME: str = "meta-llama/Llama-3-8b-hf"

    # Encryption (FERPA compliance)
    ENCRYPTION_KEY: str = "dev-encryption-key-32bytes-replace"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
