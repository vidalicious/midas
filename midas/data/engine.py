# -*- coding: utf-8 -*-
from functools import wraps
import logging
import traceback
import sys

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine


def engine(db_conf, **kwargs):
    db_url = 'mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?charset={charset}'.format(
        host=db_conf['host'],
        port=db_conf['port'],
        user=db_conf['user'],
        passwd=db_conf['passwd'],
        db=db_conf['db'],
        charset=db_conf['charset'],
    )
    return create_engine(db_url, **kwargs)


def update_to_db(session):
    def _update_to_db(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                session.rollback()
                session.remove()
                logging.error(traceback.format_exc())
                raise Exception(e)

            try:
                session.commit()
                session.remove()
            except Exception as e:
                session.rollback()
                session.remove()
                logging.error(traceback.format_exc())
                raise Exception(e)

            return result
        wrapper.__wrapped__ = func
        return wrapper

    return _update_to_db


main_config = {}
dummy = {}
# execfile(os.path.join(bin.env.config_path, "main.config"), main_config)
exec(open("./main.config").read(), dummy, main_config)

main_db = engine.engine(main_config['main_database'], pool_recycle=3600, echo=False)


# session
def _session_with_engine(bind_engine):
    return scoped_session(sessionmaker(bind=bind_engine))


main_session = _session_with_engine(main_db)
