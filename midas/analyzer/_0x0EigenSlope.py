# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.analyzer.api as api

import midas.midas.data.models as models
from midas.midas.data.engine import main_session

COL_EIGEN_SLOPE_0 = 'COL_EIGEN_SLOPE_0'
COL_EIGEN_SLOPE_1 = 'COL_EIGEN_SLOPE_1'
COL_EIGEN_SLOPE_DIFF = 'COL_EIGEN_SLOPE_DIFF'
COL_DAILY_LIMIT_COUNT = 'COL_DAILY_LIMIT_COUNT'

GAP = 5
sampling_count = 40


def main():
    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    LAST_MARKET_DATE = daily001[0].trade_date

    data_frame = DataFrame()
    for i, stock_basic in enumerate(main_session.query(models.StockBasicPro).all()):
        try:
            for key in models.StockBasicPro.keys:
                data_frame.loc[i, key] = getattr(stock_basic, key)

            daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == stock_basic.ts_code).order_by(
                models.DailyPro.trade_date.desc()).limit(sampling_count).all()
            slope0 = api.daily_weight_eigen_slope(daily=daily, begin=0, end=GAP)
            slope1 = api.daily_weight_eigen_slope(daily=daily, begin=GAP, end=GAP * 2)
            data_frame.loc[i, COL_EIGEN_SLOPE_0] = slope0
            data_frame.loc[i, COL_EIGEN_SLOPE_1] = slope1
            data_frame.loc[i, COL_EIGEN_SLOPE_DIFF] = round(slope0 - slope1, 2)
        except Exception as e:
            print('excetion in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### {i} #####'.format(i=i))

    data_frame = data_frame[
                           (data_frame[COL_EIGEN_SLOPE_0] > 0)
                           & (data_frame[COL_EIGEN_SLOPE_1] > 0)                           # & (data_frame[COL_DAILY_LIMIT_COUNT] == 0)
                           # & (data_frame[COL_ACCUMULATE_P_CHANGE] > 5)
                           # & (data_frame[COL_PRE_ACCUMULATE_P_CHANGE] < data_frame[COL_ACCUMULATE_P_CHANGE])
                           ]

    sorted_frame = data_frame.sort_values(by=COL_EIGEN_SLOPE_DIFF, ascending=False)

    file_name = '../../logs/{date}@EigenSlope.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)


if __name__ == '__main__':
    main()