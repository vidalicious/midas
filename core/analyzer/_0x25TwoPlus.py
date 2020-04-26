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
COL_LIMIT_COUNT_1 = 'COL_LIMIT_COUNT_1'
COL_LIMIT_COUNT_2 = 'COL_LIMIT_COUNT_2'
COL_LIMIT_COUNT_3 = 'COL_LIMIT_COUNT_3'
COL_LIMIT_COUNT_5 = 'COL_LIMIT_COUNT_5'
COL_FLOAT_HOLDERS = 'COL_FLOAT_HOLDERS'

sampling_count = 200


def main(offset=0):
    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    LAST_MARKET_DATE = daily001[offset].trade_date

    data_frame = DataFrame()
    for i, stock_basic in enumerate(main_session.query(models.StockBasicPro).all()):
        try:
            for key in models.StockBasicPro.keys:
                data_frame.loc[i, key] = getattr(stock_basic, key)

            daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == stock_basic.ts_code,
                                                               models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(models.DailyPro.trade_date.desc()).limit(sampling_count).all()
            data_frame.loc[i, COL_LASTPRICE] = daily[0].close
            data_frame.loc[i, COL_PCT_CHG] = daily[0].pct_chg
            data_frame.loc[i, COL_LIMIT_COUNT_1] = api.limit_chg_count(daily[:1])
            data_frame.loc[i, COL_LIMIT_COUNT_2] = api.limit_chg_count(daily[:2])
            data_frame.loc[i, COL_LIMIT_COUNT_3] = api.limit_chg_count(daily[:3])
            data_frame.loc[i, COL_LIMIT_COUNT_5] = api.limit_chg_count(daily[:5])

            holders = main_session.query(models.FloatHolderPro).filter(models.FloatHolderPro.ts_code == stock_basic.ts_code).all()
            h_list = []
            for item in holders:
                h_list.append(item.holder_name)
            data_frame.loc[i, COL_FLOAT_HOLDERS] = '\n'.join(h_list)

        except Exception as e:
            print('two plus exception in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### two plus {i} #####'.format(i=i))

    data_frame = data_frame[
                            ((data_frame[COL_LIMIT_COUNT_2] == 2) & (data_frame[COL_LIMIT_COUNT_5] == 2))
                            | ((data_frame[COL_LIMIT_COUNT_1] == 1) & (data_frame[COL_LIMIT_COUNT_3] == 2) & (data_frame[COL_LIMIT_COUNT_5] == 2))
                           ]

    data_frame = data_frame.sort_values(by=COL_PCT_CHG, ascending=True).reset_index(drop=True)
    data_frame = data_frame.loc[:, ['ts_code', 'name', 'industry', COL_PCT_CHG, COL_LASTPRICE, COL_FLOAT_HOLDERS]]

    file_name = '{logs_path}/{date}@TwoPlus.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)


if __name__ == '__main__':
    main(offset=0)