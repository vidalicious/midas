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
COL_MA_20_SLOPE_CHANGE = 'COL_MA_20_SLOPE_CHANGE'
COL_WEEKLY_BREAK = 'COL_WEEKLY_BREAK'
COL_CRIMSON_RATE = 'COL_CRIMSON_RATE'
COL_PCT_CHG_STD = 'COL_PCT_CHG_STD'
# COL_LASTPRICE = 'COL_LASTPRICE'
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

            weekly = main_session.query(models.WeeklyPro).filter(models.WeeklyPro.ts_code == stock_basic.ts_code,
                                                               models.WeeklyPro.trade_date <= LAST_MARKET_DATE).order_by(
                models.WeeklyPro.trade_date.desc()).limit(sampling_count).all()
            ma_20 = api.daily_close_ma(daily=weekly, step=20)
            ma_20_diff_1 = api.differ(ma_20)
            ma_20_diff_2 = api.differ(ma_20_diff_1)
            data_frame.loc[i, COL_MA_20] = ma_20[0]
            data_frame.loc[i, COL_MA_20_SLOPE] = ma_20_diff_1[0]
            data_frame.loc[i, COL_MA_20_SLOPE_CHANGE] = ma_20_diff_2[0]
            data_frame.loc[i, COL_WEEKLY_BREAK] = api.weekly_break(weekly[:10])

            # daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == stock_basic.ts_code,
            #                                                    models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(
            #     models.DailyPro.trade_date.desc()).limit(sampling_count).all()
            # data_frame.loc[i, COL_CRIMSON_RATE] = round(api.crimson_rate(daily[:15]), 2)
            # data_frame.loc[i, COL_PCT_CHG_STD] = round(api.pct_chg_std(daily[:15]), 2)
            holders = main_session.query(models.FloatHolderPro).filter(models.FloatHolderPro.ts_code == stock_basic.ts_code).all()
            h_list = []
            for item in holders:
                h_list.append(item.holder_name)
            data_frame.loc[i, COL_FLOAT_HOLDERS] = '\n'.join(h_list)

        except Exception as e:
            print('exception in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### tidal {i} #####'.format(i=i))

    data_frame = data_frame[
                            (data_frame[COL_WEEKLY_BREAK] == True)
                           ]
    data_frame = data_frame[
                            (data_frame[COL_MA_20_SLOPE] > 3)
                            | (data_frame[COL_MA_20_SLOPE_CHANGE] > 100)
                            # | (data_frame[COL_CRIMSON_RATE] > 0.7)
                           ]

    data_frame = data_frame.sort_values(by=COL_MA_20_SLOPE_CHANGE, ascending=False).reset_index(drop=True)
    data_frame = data_frame.loc[:, ['ts_code', 'name', 'industry', COL_MA_20, COL_MA_20_SLOPE, COL_MA_20_SLOPE_CHANGE, COL_FLOAT_HOLDERS]]

    file_name = '{logs_path}/{date}@Tidal.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)

    # data_frame = data_frame[
    #                         (data_frame[COL_MA_20_SLOPE] > 1)
    #                         & (data_frame[COL_MA_20_SLOPE_CHANGE] > 0)
    #                        ]
    # data_frame = data_frame[
    #                         (data_frame[COL_MA_20_SLOPE_CHANGE] > 100)
    #                         | (data_frame[COL_CRIMSON_RATE] > 0.7)
    #                         ]
    # data_frame = data_frame.sort_values(by=COL_MA_20_SLOPE_CHANGE, ascending=False).reset_index(drop=True)
    # file_name = '{logs_path}/{date}@Tidal_Acceleration.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    # with open(file_name, 'w', encoding='utf8') as file:
    #     data_frame.to_csv(file)
    #
    # data_frame = data_frame.sort_values(by=COL_CRIMSON_RATE, ascending=False).reset_index(drop=True)
    # file_name = '{logs_path}/{date}@Tidal_Crimson.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    # with open(file_name, 'w', encoding='utf8') as file:
    #     data_frame.to_csv(file)


if __name__ == '__main__':
    # for i in range(5, 20, 5):
    main(offset=0)