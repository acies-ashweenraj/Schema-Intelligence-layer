from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import os
import yaml
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from .paths import CONFIG_DIR, ARTIFACTS_DIR


@dataclass
class DbConfig:
    driver: str
    host: str
    port: int
    user_env: str
    password_env: str
    name: str

    @property
    def user(self) -> str:
        # Check if environment variable is set
        user_val = os.getenv(self.user_env)
        if user_val is None:
            raise ValueError(f"Environment variable '{self.user_env}' for DB user is not set.")
        return user_val

    @property
    def password(self) -> str:
        # Check if environment variable is set
        password_val = os.getenv(self.password_env)
        if password_val is None:
            raise ValueError(f"Environment variable '{self.password_env}' for DB password is not set.")
        return password_val

    @property
    def url(self) -> str:
        # Construct URL with retrieved user and password
        return f"{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class ClientConfig:
    client_id: str
    db: DbConfig
    artifacts_root: Path

    @property
    def client_artifacts_dir(self) -> Path:
        return self.artifacts_root / self.client_id


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_client_config(client_id: str) -> ClientConfig:
    cfg_path = CONFIG_DIR / f"{client_id}.yaml"
    raw = load_yaml(cfg_path)

    db_raw = raw.get("database")
    if db_raw is None:
        raise ValueError(f"Missing 'database' section in {cfg_path}")

    db_cfg = DbConfig(
        driver=db_raw["driver"],
        host=db_raw["host"],
        port=db_raw["port"],
        user_env=db_raw["user_env"],
        password_env=db_raw["password_env"],
        name=db_raw["name"],
    )

    return ClientConfig(
        client_id=raw["client_id"],
        db=db_cfg,
        artifacts_root=ARTIFACTS_DIR,
    )

class Config:
    _client_id: Optional[str] = None
    _client_config: Optional[ClientConfig] = None
    _db_engine: Optional[Engine] = None

    @classmethod
    def set_client_id(cls, client_id: str):
        if cls._client_id != client_id:
            cls._client_id = client_id
            cls._client_config = load_client_config(client_id)
            cls._db_engine = None # Reset engine if client_id changes

    @classmethod
    def get_client_config(cls) -> ClientConfig:
        if cls._client_config is None:
            raise RuntimeError("Client ID not set. Call Config.set_client_id() first.")
        return cls._client_config

    @classmethod
    def get_engine(cls) -> Engine:
        if cls._db_engine is None:
            db_url = cls.get_client_config().db.url
            cls._db_engine = create_engine(db_url)
        return cls._db_engine

    @classmethod
    def get_artifacts_dir(cls) -> Path:
        return cls.get_client_config().client_artifacts_dir

    @classmethod
    def get_config_dir(cls) -> Path:
        return CONFIG_DIR