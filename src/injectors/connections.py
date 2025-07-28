from base_module.injectors import PgConnectionInj
from config import settings
from models import *  # noqa

pg = PgConnectionInj(
    conf=settings.to_pg_config(),
)
