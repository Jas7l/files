import dataclasses as dc
import typing
from datetime import datetime

import sqlalchemy as sa
from base_module.models import BaseOrmMappedModel

SCHEMA_NAME = 'files'

@dc.dataclass
class File(BaseOrmMappedModel):
    """SQL модель файла"""

    __tablename__ = 'files'
    __table_args__ = {'schema': SCHEMA_NAME}

    id: int = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.Integer, autoincrement=True, primary_key=True
        )},
    )
    name: str = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.String(100), nullable=False
        )},
    )
    extension: str = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.String(10), nullable=False
        )},
    )
    stored_name: str = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.String(64), nullable=False, unique=True
        )},
    )
    size: int = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.Integer, nullable=False
        )},
    )
    path: str = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.String(100), nullable=False
        )},
    )
    creation_date: datetime = dc.field(
        default_factory=datetime.utcnow,
        metadata={'sa': sa.Column(
            sa.DateTime(),
        )},
    )
    update_date: typing.Optional[datetime] = dc.field(
        default_factory=datetime.utcnow,
        metadata={'sa': sa.Column(
            sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()
        )},
    )
    comment: typing.Optional[str] = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.String(200), nullable=True
        )},
    )
    owner_id: int = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.BigInteger,
            sa.ForeignKey(
                'files.users.id',
                ondelete='CASCADE',
                use_alter=True,
                name='fk_owner_id',
            ),
            nullable=False,
        )}
    )
    relative_path: str = dc.field(
        default=None,
        metadata={'sa': sa.Column(
            sa.Text, nullable=True
        )},
    )


BaseOrmMappedModel.REGISTRY.mapped(File)
