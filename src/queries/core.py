import sys
from os.path import dirname, abspath

sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))

from models import metadata
from database import sync_engine, sync_session
from sqlalchemy import insert, select
from sqlalchemy.orm import joinedload

from models import Characteristics_BTCUSDT


def create_table():
    metadata.create_all(sync_engine)


def drop_table():
    metadata.drop_all(sync_engine)


def insert_info_table(table, data):
    with sync_engine.connect() as conn:
        stmt = insert(table).values(data)
        conn.execute(stmt)
        conn.commit()


def select_data(Model_select):
    with sync_session() as session:
        query = select(Model_select)
        result = session.execute(query).all()
    return result

