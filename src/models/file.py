import dataclasses as dc
import typing
from datetime import datetime

import sqlalchemy as sa
from .model import BaseOrmMappedModel

SCHEMA_NAME = 'files'


@dc.dataclass
class File(BaseOrmMappedModel):
    """."""

    __tablename__ = "files"

    id: int = dc.field(
        default=None,
        metadata={"sa": sa.Column(sa.Integer, autoincrement=True, primary_key=True)}
    )
    name: str = dc.field(
        default=None,
        metadata={"sa": sa.Column(sa.String(100), nullable=False)}
    )
    extension: str = dc.field(
        default=None,
        metadata={"sa": sa.Column(sa.String(10), nullable=False)}
    )
    size: int = dc.field(
        default=None,
        metadata={"sa": sa.Column(sa.Integer, nullable=False)}

    )
    path: str = dc.field(
        default=None,
        metadata={"sa": sa.Column(sa.String(100), nullable=False)}
    )
    creation_date: datetime = dc.field(
        default_factory=datetime.utcnow,
        metadata={"sa": sa.Column(sa.DateTime())}
    )
    update_date: typing.Optional[datetime] = dc.field(
        default_factory=datetime.utcnow,
        metadata={"sa": sa.Column(sa.DateTime, server_default=sa.func.now(),onupdate=sa.func.now())}
    )
    comment: typing.Optional[str] = dc.field(
        default=None,
        metadata={"sa": sa.Column(sa.String(200), nullable=True)}
    )


BaseOrmMappedModel.REGISTRY.mapped(File)
