# -*- coding: utf-8 -*-
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Boolean, Integer, Text, String, BIGINT, DateTime, Float
from midas.core.data.engine import main_db


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


class DailyPro(Base):
    __tablename__ = "daily_pro"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    ts_code = Column(String(100))
    trade_date = Column(Integer)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    pre_close = Column(Float)
    change = Column(Float)
    pct_chg = Column(Float)
    vol = Column(Float)
    amount = Column(Float)


class WeeklyPro(Base):
    __tablename__ = "weekly_pro"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    ts_code = Column(String(100))
    trade_date = Column(Integer)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    pre_close = Column(Float)
    change = Column(Float)
    pct_chg = Column(Float)
    vol = Column(Float)
    amount = Column(Float)


class DailyBasicPro(Base):
    __tablename__ = "daily_basic_pro"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    ts_code = Column(String(100))
    trade_date = Column(Integer)
    turnover_rate = Column(Float)  # 换手率
    turnover_rate_f = Column(Float)  # 换手率（自由流通股）
    total_share = Column(Float)  # 总股本（万股）
    float_share = Column(Float)  # 流通股本（万股）
    free_share = Column(Float)  # 自由流通股本（万）
    total_mv = Column(Float)  # 总市值（万元）
    circ_mv = Column(Float)  # 流通市值（万元）


class StockCompanyPro(Base):
    __tablename__ = "stock_company_pro"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    ts_code = Column(String(100))
    main_business = Column(String(2000))
    business_scope = Column(String(2000))


class ConceptPro(Base):
    __tablename__ = "concept_pro"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    code = Column(String(100))
    name = Column(String(100))

    keys = ['code', 'name']


class ConceptDetailPro(Base):
    __tablename__ = "concept_detail_pro"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    code = Column(String(100))
    ts_code = Column(String(100))
    name = Column(String(100))


class StockLive(Base):
    __tablename__ = "stock_live"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    ts_code = Column(String(100))
    chg = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.now)


StockBasicPro.metadata.tables["stock_basic_pro"].create(bind=main_db, checkfirst=True)
DailyPro.metadata.tables["daily_pro"].create(bind=main_db, checkfirst=True)
WeeklyPro.metadata.tables["weekly_pro"].create(bind=main_db, checkfirst=True)
DailyBasicPro.metadata.tables["daily_basic_pro"].create(bind=main_db, checkfirst=True)
StockCompanyPro.metadata.tables["stock_company_pro"].create(bind=main_db, checkfirst=True)
ConceptPro.metadata.tables["concept_pro"].create(bind=main_db, checkfirst=True)
ConceptDetailPro.metadata.tables["concept_detail_pro"].create(bind=main_db, checkfirst=True)
StockLive.metadata.tables["stock_live"].create(bind=main_db, checkfirst=True)