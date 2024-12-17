import datetime
import enum
from time import strftime
from typing import Annotated

from sqlalchemy import MetaData, Table, Column, Integer, DateTime, Float, ForeignKey, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

"Декларативная  таблица"


class Base(DeclarativeBase):
    pass


intpk = Annotated[int, mapped_column(primary_key=True)]
bool_value = Annotated[bool, mapped_column(default=False)]


class BTCUSDT_table_ORM(Base):
    __tablename__  = 'BTCUSDT_table_day'
    id: Mapped[intpk]
    date: Mapped[datetime.datetime]
    open_prise: Mapped[float]
    close_prise: Mapped[float]
    height_prise: Mapped[float]
    low_prise: Mapped[float]
    characteristic: Mapped["Characteristics_BTCUSDT_ORM"] = relationship(
        back_populates="BTCUSDT",
        uselist=False
    )

    def __str__(self):
        return f'BTCUSDT({self.date.strftime("%Y-%m-%d")})'

    def __repr__(self):
        return self.__str__()


class Characteristics_BTCUSDT_ORM(Base):
    __tablename__ = "BTCUSDT_charact"
    id: Mapped[intpk]
    BTCUSDT_id: Mapped[int] = mapped_column(ForeignKey("BTCUSDT_table_day.id", ondelete="CASCADE"))
    BTCUSDT: Mapped["BTCUSDT_table_ORM"] = relationship(
        back_populates="characteristic",
        uselist=False
    )
    relative_height_30: Mapped[bool_value]
    relative_low_30: Mapped[bool_value]
    relative_height_20: Mapped[bool_value]
    relative_low_20: Mapped[bool_value]
    relative_height_10: Mapped[bool_value]
    relative_low_10: Mapped[bool_value]
    relative_height_5: Mapped[bool_value]
    relative_low_5: Mapped[bool_value]
    relative_height_1: Mapped[bool_value]
    relative_low_1: Mapped[bool_value]


"Императивная таблица"

metadata = MetaData()

BTCUSDT_table_day = Table(
    'BTCUSDT_table_day',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('date', DateTime),
    Column('open_prise', Float),
    Column('close_prise', Float),
    Column('height_prise', Float),
    Column('low_prise', Float),
)


Characteristics_BTCUSDT = Table(
    'BTCUSDT_charact',
    metadata,
    Column('BTCUSDT_id', ForeignKey('BTCUSDT_table_day.id', ondelete='CASCADE')),
    Column('id', Integer, primary_key=True),
    Column('relative_height_30', BOOLEAN, default=False),
    Column('relative_low_30', BOOLEAN, default=False),
    Column('relative_height_20', BOOLEAN, default=False),
    Column('relative_low_20', BOOLEAN, default=False),
    Column('relative_height_10', BOOLEAN, default=False),
    Column('relative_low_10', BOOLEAN, default=False),
    Column('relative_height_5', BOOLEAN, default=False),
    Column('relative_low_5', BOOLEAN, default=False),
    Column('relative_height_1', BOOLEAN, default=False),
    Column('relative_low_1', BOOLEAN, default=False),
)