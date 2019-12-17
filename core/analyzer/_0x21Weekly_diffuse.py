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
COL_ACCUMULATE = 'COL_ACCUMULATE'
COL_CONTINUOUS_COUNT = 'COL_CONTINUOUS_COUNT'
COL_DAILY_VIBRATION = 'COL_DAILY_VIBRATION'
COL_DAILY_AGGRESSIVE_ACCUMULATION = 'COL_DAILY_AGGRESSIVE_ACCUMULATION'
COL_DAILY_NEGATIVE_ACCUMULATION = 'COL_DAILY_NEGATIVE_ACCUMULATION'
COL_DAILY_AGGRESSIVE_RATE = 'COL_DAILY_AGGRESSIVE_RATE'
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
            data_frame.loc[i, COL_MA_20] = ma_20[0]
            data_frame.loc[i, COL_MA_20_SLOPE] = round(ma_20_diff_1[0], 2)
            # continuous_count = api.continuous_positive_count(ma_20_diff_1)
            # data_frame.loc[i, COL_CONTINUOUS_COUNT] = continuous_count
            # data_frame.loc[i, COL_ACCUMULATE] = round(weekly[0].close / weekly[continuous_count].close, 2)
            # data_frame.loc[i, COL_LASTPRICE] = weekly[0].close

            daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == stock_basic.ts_code,
                                                               models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(models.DailyPro.trade_date.desc()).limit(sampling_count).all()
            # data_frame.loc[i, COL_DAILY_VIBRATION] = round(api.avg_vibration_chg(daily[:20]), 2)
            data_frame.loc[i, COL_LASTPRICE] = daily[0].close
            data_frame.loc[i, COL_DAILY_AGGRESSIVE_ACCUMULATION] = round(api.aggressive_chg_accumulation(daily[:5]), 2)
            data_frame.loc[i, COL_DAILY_NEGATIVE_ACCUMULATION] = round(api.negative_chg_accumulation(daily[:5]), 2)

            if data_frame.loc[i, COL_DAILY_NEGATIVE_ACCUMULATION] < 0:
                data_frame.loc[i, COL_DAILY_AGGRESSIVE_RATE] = round(- data_frame.loc[i, COL_DAILY_AGGRESSIVE_ACCUMULATION] / data_frame.loc[i, COL_DAILY_NEGATIVE_ACCUMULATION], 2)
            else:
                data_frame.loc[i, COL_DAILY_AGGRESSIVE_RATE] = round(data_frame.loc[i, COL_DAILY_AGGRESSIVE_ACCUMULATION], 2)

            holders = main_session.query(models.FloatHolderPro).filter(models.FloatHolderPro.ts_code == stock_basic.ts_code).all()
            h_list = []
            for item in holders:
                h_list.append(item.holder_name)
            data_frame.loc[i, COL_DAILY_AGGRESSIVE_RATE] = '\n'.join(h_list)

        except Exception as e:
            print('excetion in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### {i} #####'.format(i=i))

    data_frame = data_frame[
                            (data_frame[COL_MA_20_SLOPE] > 0)
                            & (data_frame[COL_MA_20_SLOPE] > 2)
                            # & (data_frame[COL_DAILY_VIBRATION] > 5)
                            & (data_frame[COL_DAILY_AGGRESSIVE_RATE] > 0)
                           ]
    # data_frame = data_frame.sort_values(by=COL_MAXGAP, ascending=False).reset_index(drop=True)
    # data_frame = data_frame.iloc[:200]

    data_frame = data_frame.sort_values(by=COL_DAILY_AGGRESSIVE_RATE, ascending=False).reset_index(drop=True)
    data_frame = data_frame.loc[:, ['ts_code', 'name', 'industry', COL_LASTPRICE, COL_MA_20_SLOPE, COL_ACCUMULATE,
                                     COL_DAILY_AGGRESSIVE_ACCUMULATION, COL_DAILY_AGGRESSIVE_RATE, COL_FLOAT_HOLDERS]]

    file_name = '{logs_path}/{date}@Weekly_diffuse.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)


if __name__ == '__main__':
    main(offset=0)