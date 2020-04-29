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
COL_DAILY_AGGRESSIVE_ACCUMULATION = 'COL_DAILY_AGGRESSIVE_ACCUMULATION'
COL_FLOAT_HOLDERS = 'COL_FLOAT_HOLDERS'

sampling_count = 200


def main(offset=0):
    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    LAST_MARKET_DATE = daily001[offset].trade_date

    data_frame = DataFrame()
    for i, stock_basic in enumerate(main_session.query(models.StockBasicPro).all()):
        if stock_basic.ts_code.startswith('688'):
            continue
        try:
            for key in models.StockBasicPro.keys:
                data_frame.loc[i, key] = getattr(stock_basic, key)

            daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == stock_basic.ts_code,
                                                               models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(models.DailyPro.trade_date.desc()).limit(sampling_count).all()
            data_frame.loc[i, COL_LASTPRICE] = daily[0].close
            data_frame.loc[i, COL_PCT_CHG] = daily[0].pct_chg
            data_frame.loc[i, COL_DAILY_AGGRESSIVE_ACCUMULATION] = round(api.aggressive_chg_accumulation(daily[:15]), 2)

            holders = main_session.query(models.FloatHolderPro).filter(models.FloatHolderPro.ts_code == stock_basic.ts_code).all()
            h_list = []
            for item in holders:
                h_list.append(item.holder_name)
            data_frame.loc[i, COL_FLOAT_HOLDERS] = '\n'.join(h_list)

        except Exception as e:
            print('wind chime exception in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### wind chime {i} #####'.format(i=i))

    data_frame = data_frame.reset_index(drop=True)

    up_count = 0
    down_count = 0
    up_limit_count = 0
    down_limit_count = 0
    limit_count_1 = 0
    limit_count_2 = 0
    limit_count_3 = 0
    limit_count_4 = 0
    limit_count_over5 = 0
    max_limit_count = 0
    max_limit_stock = None

    for i in range(len(data_frame)):
        if data_frame.loc[i, COL_PCT_CHG] > 0:
            up_count += 1
        else:
            down_count += 1

        if data_frame.loc[i, COL_PCT_CHG] > 9.8:
            up_limit_count += 1

            accumulate_limit_count = data_frame.loc[i, COL_DAILY_AGGRESSIVE_ACCUMULATION] / 9.8
            if accumulate_limit_count > 4:
                limit_count_over5 += 1
            elif accumulate_limit_count > 3:
                limit_count_4 += 1
            elif accumulate_limit_count > 2:
                limit_count_3 += 1
            elif accumulate_limit_count > 1:
                limit_count_2 += 1
            else:
                limit_count_1 += 1

            if data_frame.loc[i, COL_DAILY_AGGRESSIVE_ACCUMULATION] / 9.8 > max_limit_count:
                max_limit_count = int(data_frame.loc[i, COL_DAILY_AGGRESSIVE_ACCUMULATION] / 9.8)
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
        limit_count_1=limit_count_1,
        limit_count_2=limit_count_2,
        limit_count_3=limit_count_3,
        limit_count_4=limit_count_4,
        limit_count_over5=limit_count_over5,
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
    # for i in range(20, -1, -1):
    #     main(offset=i)
    main(offset=0)