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


COL_MA_20 = 'COL_MA_20'
COL_MA_20_SLOPE = 'COL_MA_20_SLOPE'
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
            daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == stock_basic.ts_code,
                                                               models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(models.DailyPro.trade_date.desc()).limit(sampling_count).all()
            # 新股
            if len(daily) < 30:
                continue
            for key in models.StockBasicPro.keys:
                data_frame.loc[i, key] = getattr(stock_basic, key)
            data_frame.loc[i, COL_LASTPRICE] = daily[0].close
            data_frame.loc[i, COL_PCT_CHG] = daily[0].pct_chg
            data_frame.loc[i, COL_DAILY_AGGRESSIVE_ACCUMULATION] = round(api.aggressive_chg_accumulation(daily[:15]), 2)

            holders = main_session.query(models.FloatHolderPro).filter(models.FloatHolderPro.ts_code == stock_basic.ts_code).all()
            h_list = []
            for item in holders:
                h_list.append(item.holder_name)
            data_frame.loc[i, COL_FLOAT_HOLDERS] = '\n'.join(h_list)

        except Exception as e:
            print('demon hunter exception in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### demon hunter {i} #####'.format(i=i))

    data_frame = data_frame[
                            (data_frame[COL_PCT_CHG] > 9)
                           ]

    data_frame = data_frame.sort_values(by=COL_DAILY_AGGRESSIVE_ACCUMULATION, ascending=False).reset_index(drop=True)
    data_frame = data_frame.loc[:, ['ts_code', 'name', 'industry', COL_PCT_CHG, COL_LASTPRICE,
                                    COL_DAILY_AGGRESSIVE_ACCUMULATION, COL_FLOAT_HOLDERS]]

    file_name = '{logs_path}/{date}@demon_hunter.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)

    # df_limit = data_frame[
    #                         (data_frame[COL_PCT_CHG] > 9)
    #                      ]
    # file_name = '{logs_path}/{date}@demon_hunter_hot.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    # with open(file_name, 'w', encoding='utf8') as file:
    #     df_limit.to_csv(file)


if __name__ == '__main__':
    main(offset=0)