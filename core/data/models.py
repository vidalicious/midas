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


class DailyBasic(Base):
    __tablename__ = "daily_basic"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    symbol = Column(String(100))
    name = Column(String(100))
    trade_date = Column(Integer)
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


class FloatHolderPro(Base):
    __tablename__ = "float_holder_pro"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    ts_code = Column(Integer)
    ann_date = Column(Integer)
    holder_name = Column(String(200))


class StockLive(Base):
    __tablename__ = "stock_live"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    ts_code = Column(String(100))
    chg = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.now)


class Analyst(Base):
    __tablename__ = "analyst"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    trade_date = Column(Integer)
    up_count = Column(Integer)
    down_count = Column(Integer)
    up_limit_count = Column(Integer)
    down_limit_count = Column(Integer)
    limit_count_1 = Column(Integer)
    limit_count_2 = Column(Integer)
    limit_count_3 = Column(Integer)
    limit_count_4 = Column(Integer)
    limit_count_over5 = Column(Integer)
    max_limit_count = Column(Integer)
    max_limit_stock = Column(String(100))

    keys = ['trade_date', 'up_count', 'down_count', 'up_limit_count', 'down_limit_count', 'limit_count_1',
            'limit_count_2', 'limit_count_3', 'limit_count_4', 'limit_count_over5', 'max_limit_count', 'max_limit_stock']


StockBasicPro.metadata.tables["stock_basic_pro"].create(bind=main_db, checkfirst=True)
DailyPro.metadata.tables["daily_pro"].create(bind=main_db, checkfirst=True)
WeeklyPro.metadata.tables["weekly_pro"].create(bind=main_db, checkfirst=True)
DailyBasicPro.metadata.tables["daily_basic_pro"].create(bind=main_db, checkfirst=True)
DailyBasic.metadata.tables["daily_basic"].create(bind=main_db, checkfirst=True)

StockCompanyPro.metadata.tables["stock_company_pro"].create(bind=main_db, checkfirst=True)
ConceptPro.metadata.tables["concept_pro"].create(bind=main_db, checkfirst=True)
ConceptDetailPro.metadata.tables["concept_detail_pro"].create(bind=main_db, checkfirst=True)
FloatHolderPro.metadata.tables["float_holder_pro"].create(bind=main_db, checkfirst=True)
Analyst.metadata.tables["analyst"].create(bind=main_db, checkfirst=True)

StockLive.metadata.tables["stock_live"].create(bind=main_db, checkfirst=True)