from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings

sync_engine = create_engine(
    url=settings.DB_URL,
    echo=False
)

sync_session = sessionmaker(sync_engine)

