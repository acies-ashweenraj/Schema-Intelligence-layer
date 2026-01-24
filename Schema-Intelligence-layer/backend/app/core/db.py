from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine

from .config import DbConfig


def create_db_engine(db: DbConfig) -> Engine:
    return create_engine(db.url)


def get_inspector(engine: Engine):
    return inspect(engine)
