from sqlalchemy import URL, create_engine
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, sessionmaker

import config

DB_URI = URL.create(
    config.RDBMS + "+" + config.DBAPI,
    **config.DB_CONFIG,
)

engine = create_engine(DB_URI)
LocalSession = sessionmaker(engine)


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls):
        return "".join(
            [
                "_" + c if c.isupper() and not cls.__name__.startswith(c) else c
                for c in cls.__name__
            ]
        ).lower()

    def __repr__(self):
        return f"<{type(self).__name__} {self.id}>"
