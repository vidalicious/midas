# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.core.analyzer.api as api

import midas.core.data.models as models
from midas.core.data.engine import main_session

COL_LASTPRICE = 'COL_LASTPRICE'
COL_FITNESS = 'COL_FITNESS'

GAP = 10
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
            data_frame.loc[i, COL_LASTPRICE] = daily[0].close
            score = 0
            for j in range(3):
                score = score + api.daily_weight_exponential_fitness(daily=daily, begin=j, end=j + GAP, exp=1)
            data_frame.loc[i, COL_FITNESS] = round(score, 2)
        except Exception as e:
            print('excetion in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### {i} #####'.format(i=i))

    # data_frame = data_frame[
    #                        (data_frame[COL_EIGEN_SLOPE_0] > 0)
    #                        & (data_frame[COL_EIGEN_SLOPE_1] > 0)                           # & (data_frame[COL_DAILY_LIMIT_COUNT] == 0)
    #                        # & (data_frame[COL_ACCUMULATE_P_CHANGE] > 5)
    #                        # & (data_frame[COL_PRE_ACCUMULATE_P_CHANGE] < data_frame[COL_ACCUMULATE_P_CHANGE])
    #                        ]

    sorted_frame = data_frame.sort_values(by=COL_FITNESS, ascending=False).reset_index(drop=True)

    file_name = '../../logs/{date}@Regression_exp1.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)


if __name__ == '__main__':
    main()