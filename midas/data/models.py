# -*- coding: utf-8 -*-
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Boolean, Integer, Text, String, BIGINT, DateTime

class Base(declarative_base()):
    __abstract__ = True
    __table_args__ = (
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8'
        }
    )


class StockBasicPro(Base):
    __tablename__ = "stock_basic_pro"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    ts_code = Column(String(100))
    symbol = Column(String(100))
    name = Column(String(100))
    industry = Column(String(100))

    keys = ['ts_code', 'symbol', 'name', 'industry']