"""SQLAlchemy 2.0 session & engine management (PostgreSQL + pgvector ready, SQLite local dev)."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.app.config import get_settings


class Base(DeclarativeBase):
    pass


def build_engine(database_url: str | None = None) -> Engine:
    url = database_url or get_settings().database_url
    connect_args: dict[str, object] = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        if url.startswith("sqlite:///") and not url.endswith(":memory:"):
            db_path = Path(url.replace("sqlite:///", "", 1))
            db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(url, connect_args=connect_args, future=True)


engine = build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_db(target_engine: Engine | None = None) -> None:
    """Create all tables idempotently and apply safe additive column upgrades for SQLite dev DBs."""
    from sqlalchemy import inspect, text

    from backend.app.db import models  # noqa: F401

    eng = target_engine or engine
    Base.metadata.create_all(bind=eng)

    if eng.dialect.name == "sqlite":
        inspector = inspect(eng)
        migrations = [
            ("reading_tests", "is_drill_bank", "BOOLEAN DEFAULT 0"),
            ("reading_tests", "drill_slot", "INTEGER"),
            ("question_items", "listening_test_id", "VARCHAR(64)"),
            ("user_attempts", "diagnostic_detail", "VARCHAR(512)"),
        ]
        with eng.begin() as conn:
            for table_name, col_name, col_def in migrations:
                if inspector.has_table(table_name):
                    existing_cols = {c["name"] for c in inspector.get_columns(table_name)}
                    if col_name not in existing_cols:
                        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}"))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
