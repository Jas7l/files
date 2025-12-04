import dataclasses as dc
from datetime import datetime

import sqlalchemy as sa
from base_module.models import BaseOrmMappedModel
from passlib.hash import bcrypt

SCHEMA_NAME = 'files'


@dc.dataclass
class User(BaseOrmMappedModel):
    """SQL модель пользователя"""

    __tablename__ = 'users'
    __table_args__ = {'schema': SCHEMA_NAME}

    id: int = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.BigInteger, primary_key=True, autoincrement=True
        )},
    )
    username: str = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.String(100), nullable=False, unique=True
        )},
    )
    password_hash: str = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.String(255), nullable=False
        )},
    )
    created_at: datetime = dc.field(
        default_factory=datetime.utcnow,
        metadata={'sa': sa.Column(
            sa.DateTime(), server_default=sa.func.now()
        )},
    )

    def verify_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.password_hash)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hash(password)


BaseOrmMappedModel.REGISTRY.mapped(User)
