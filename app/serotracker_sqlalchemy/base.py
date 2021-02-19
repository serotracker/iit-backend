import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import current_app as app

logger = logging.getLogger(__name__)


def delete_records(session, records):
    for record in records:
        session.delete(record)
    session.commit()
    return


@contextmanager
def db_session():
    engine_url = app.config['SQLALCHEMY_DATABASE_URI']
    engine = create_engine(engine_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    except Exception as e:
        logging.debug('Database session exception occurred: {}'.format(e))
        session.rollback()
        raise e
    finally:
        session.close()
