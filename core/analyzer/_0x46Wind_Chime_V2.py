# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.core.analyzer.api as api

import midas.core.data.models as models
from midas.core.data.engine import main_session
import midas.bin.env as env


COL_LASTPRICE = 'COL_LASTPRICE'
COL_PCT_CHG = 'COL_PCT_CHG'
COL_BLAST_BOARD = 'COL_BLAST_BOARD'
COL_CONTINUOUS_LIMIT_COUNT = 'COL_CONTINUOUS_LIMIT_COUNT'

sampling_count = 200


def main(offset=0):
    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    LAST_MARKET_DATE = daily001[offset].trade_date

    data_frame = DataFrame()
    for i, stock_basic in enumerate(main_session.query(models.StockBasicPro).all()):
        try:
            daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == stock_basic.ts_code,
                                                               models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(models.DailyPro.trade_date.desc()).limit(sampling_count).all()
            if len(daily) < 30:
                continue
            for key in models.StockBasicPro.keys:
                data_frame.loc[i, key] = getattr(stock_basic, key)
            data_frame.loc[i, COL_LASTPRICE] = daily[0].close
            data_frame.loc[i, COL_PCT_CHG] = daily[0].pct_chg

            highest_chg = (daily[0].high / daily[0].pre_close - 1) * 100
            data_frame.loc[i, COL_BLAST_BOARD] = highest_chg > 9.8 and daily[0].pct_chg < 9.8
            data_frame.loc[i, COL_CONTINUOUS_LIMIT_COUNT] = api.daily_continuous_limit_count(daily)

        except Exception as e:
            print('wind chime exception in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### wind chime {i} #####'.format(i=i))

    data_frame = data_frame.reset_index(drop=True)

    up_count = 0
    down_count = 0
    up_limit_count = 0
    down_limit_count = 0
    blast_board_count = 0
    limit_count_1 = 0
    limit_count_2 = 0
    limit_count_3 = 0
    limit_count_over3 = 0
    max_limit_count = 0
    max_limit_stock = None

    for i in range(len(data_frame)):
        if data_frame.loc[i, COL_PCT_CHG] > 0:
            up_count += 1
        else:
            down_count += 1

        if data_frame.loc[i, COL_BLAST_BOARD]:
            blast_board_count += 1

        if data_frame.loc[i, COL_PCT_CHG] > 9.8:
            up_limit_count += 1

            if data_frame.loc[i, COL_CONTINUOUS_LIMIT_COUNT] > 3:
                limit_count_over3 += 1
            elif data_frame.loc[i, COL_CONTINUOUS_LIMIT_COUNT] > 2:
                limit_count_3 += 1
            elif data_frame.loc[i, COL_CONTINUOUS_LIMIT_COUNT] > 1:
                limit_count_2 += 1
            else:
                limit_count_1 += 1

            if data_frame.loc[i, COL_CONTINUOUS_LIMIT_COUNT] > max_limit_count:
                max_limit_count = int(data_frame.loc[i, COL_CONTINUOUS_LIMIT_COUNT])
                max_limit_stock = '{ts_code} {name}'.format(ts_code=data_frame.loc[i, 'ts_code'], name=data_frame.loc[i, 'name'])

        if data_frame.loc[i, COL_PCT_CHG] < -9.8:
            down_limit_count += 1

        print('wind chime analyse in index:{index}'.format(index=i))

    main_session.query(models.Analyst).filter(models.Analyst.trade_date == LAST_MARKET_DATE).delete()
    a_analyst = models.Analyst(
        trade_date=LAST_MARKET_DATE,
        up_count=up_count,
        down_count=down_count,
        up_limit_count=up_limit_count,
        down_limit_count=down_limit_count,
        blast_board_count=blast_board_count,
        limit_count_1=limit_count_1,
        limit_count_2=limit_count_2,
        limit_count_3=limit_count_3,
        limit_count_over3=limit_count_over3,
        max_limit_count=max_limit_count,
        max_limit_stock=max_limit_stock
    )

    main_session.add(a_analyst)
    main_session.commit()

    analysts = main_session.query(models.Analyst).order_by(models.Analyst.trade_date.desc()).all()
    analyst_df = DataFrame()
    for i, analyst in enumerate(analysts):
        for key in models.Analyst.keys:
            analyst_df.loc[i, key] = getattr(analyst, key)

    file_name = '{logs_path}/{date}@WindChime.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    with open(file_name, 'w', encoding='utf8') as file:
        analyst_df.to_csv(file)

        
if __name__ == '__main__':
    main(offset=0)