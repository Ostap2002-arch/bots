import sys
from datetime import datetime
from os.path import dirname, abspath

from sqlalchemy import select, update, and_
from sqlalchemy.orm import joinedload
from typing import Optional, Type

sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))

from src.models import Characteristics_BTCUSDT_ORM, BTCUSDT_table_ORM
from src.models import Base
from src.database import sync_engine, sync_session


def create_table_all():
    Base.metadata.create_all(sync_engine)


def drop_table_all():
    Base.metadata.drop_all(sync_engine)


def drop_table(drop_table):
    with sync_engine.connect() as conn:
        drop_table.__table__.drop(conn, checkfirst=True)
        conn.commit()
        print(f'{drop_table} удалена')


def create_table(create_table):
    with sync_engine.connect() as conn:
        create_table.__table__.create(conn, checkfirst=True)
        conn.commit()
        print(f'{drop_table} создана')


def select_data_orm(Model_select_orm):
    with sync_session() as session:
        query = select(Model_select_orm).options(joinedload(Model_select_orm.characteristic)).order_by(
            Model_select_orm.id)
        result = session.execute(query).scalars().all()
    return result


def select_data_by_date(Model_select_orm: Type[BTCUSDT_table_ORM], start: Optional[datetime], stop: Optional[datetime]) -> list:
    """Функция возвращает список бар

    Функция принимает на вход две даты (необязательно заданы) и возвращается список всех бар между указанными числами.
    Если на вход не будут заданны start и stop функция вернёт все записи, как это бы сделала select_data_orm.

    Args:
        Model_select_orm (Type[BTCUSDT_table_ORM]): Модель таблицы базы данных
        start (Optional[datetime]): Дата начала списка (опционально)
        stop (Optional[datetime]): Дата конца списка (опционально)

    Returns:
        list: Список бар между датами
    """
    with sync_session() as session:
        if start and stop:
            query = select(Model_select_orm).filter(
                and_(start <= Model_select_orm.date, Model_select_orm.date <= stop)).order_by(Model_select_orm.id)
        elif start:
            query = select(Model_select_orm).filter(start <= Model_select_orm.date).order_by(Model_select_orm.id)
        elif stop:
            query = select(Model_select_orm).filter(stop >= Model_select_orm.date).order_by(Model_select_orm.id)
        else:
            return select_data_orm(Model_select_orm)
        result = session.execute(query).scalars().all()
        return result


# def select_data_orm_with_date(Model_select_orm, date1: datetime, date2: datetime):
#     with sync_session() as session:
#         query = select(Model_select_orm).options(joinedload(Model_select_orm.characteristic)).order_by(
#             Model_select_orm.id).filter(and_(date1 < Model_select_orm.date,  Model_select_orm.date < date2))
#         result = session.execute(query).scalars().all()


def clear_table_orm(Table_orm):
    with sync_session() as session:
        session.execute(Table_orm.__table__.delete())
        session.commit()


def insert_info_table_orm(Model_info_add, *values, **kwargs):
    with sync_session() as session:
        new_record = Model_info_add(**kwargs)
        new_record.characteristic = Characteristics_BTCUSDT_ORM()
        session.add(new_record)
        session.commit()


def update_table(Model_table_update, **kwargs):
    with sync_session() as session:
        stmt = update(Characteristics_BTCUSDT_ORM).filter(
            Characteristics_BTCUSDT_ORM.BTCUSDT_id == Model_table_update.id).values(**kwargs)
        session.execute(stmt)
        session.commit()
