import dataclasses as dc
import os

import yaml

from base_module.config import PgConfig
from base_module.models import Model


@dc.dataclass
class AppConfig(Model):
    pg: PgConfig
    storage_path: str = dc.field(default="/app/storage")
    sync_interval: int = dc.field(default=3600)
    debug: bool = dc.field(default=False)


config: AppConfig = AppConfig.load(
    yaml.safe_load(open(os.getenv('YAML_PATH', "/app/config.yaml"))) or {}
)
