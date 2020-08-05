import logging
from contextlib import contextmanager

from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


@contextmanager
def db_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    except Exception as e:
        logging.debug('Database session exception occurred: {}'.format(e))
        session.rollback()
    finally:
        session.close()
