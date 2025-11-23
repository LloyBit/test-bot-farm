"""ORM схемы для Postgres."""
from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, String, Enum as SQLAlchemyEnum
# Быстрее чем UUID из алхимии
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

from app.infrastructure.db.migration import Base

class Env(str, Enum):
    prod = "prod"
    preprod = "preprod"
    stage = "stage"


class Domain(str, Enum):
    canary = "canary"
    regular = "regular"


class User(Base):
    __tablename__ = "users"

    id = Column(PostgresUUID, primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.now)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)
    project_id = Column(PostgresUUID, nullable=False)
    env = Column(SQLAlchemyEnum(Env), nullable=False)
    domain = Column(SQLAlchemyEnum(Domain), nullable=False)
    locktime = Column(Integer, nullable=False, default=0)