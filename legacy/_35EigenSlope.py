# -*- coding: utf-8 -*-
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.legacy.api_pro as api

COL_EIGEN_SLOPE_0 = 'COL_EIGEN_SLOPE_0'
COL_EIGEN_SLOPE_1 = 'COL_EIGEN_SLOPE_1'
COL_EIGEN_SLOPE_DIFF = 'COL_EIGEN_SLOPE_DIFF'
COL_DAILY_LIMIT_COUNT = 'COL_DAILY_LIMIT_COUNT'

GAP = 5

sampling_count = 100


def main():
    pro = ts.pro_api()

    trade_dates = pro.daily(ts_code='000001.SZ').trade_date
    LAST_MARKET_DATE = trade_dates[2]

    stock_basic = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,industry,fullname')

    data_frame = DataFrame()
    for key in ['ts_code', 'name', 'industry']:
        data_frame[key] = stock_basic[key]

    for key in [COL_EIGEN_SLOPE_0, COL_EIGEN_SLOPE_1, COL_EIGEN_SLOPE_DIFF, COL_DAILY_LIMIT_COUNT, 'circ_mv']:
        data_frame[key] = np.nan

    for i, ts_code in enumerate(data_frame.ts_code):
        try:
            daily_basic = pro.daily_basic(ts_code=ts_code,          #trade_date=LAST_MARKET_DATE
                                          start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
            for key in ['circ_mv', ]:
                data_frame.loc[i, key] = daily_basic.loc[0, key]

            daily = pro.daily(ts_code=ts_code, start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
            data_frame.loc[i, COL_EIGEN_SLOPE_0] = api.daily_weight_eigen_slope(daily=daily, begin=0, end=GAP)
            data_frame.loc[i, COL_EIGEN_SLOPE_1] = api.daily_weight_eigen_slope(daily=daily, begin=GAP, end=GAP * 2)
            data_frame.loc[i, COL_EIGEN_SLOPE_DIFF] = round(data_frame.loc[i, COL_EIGEN_SLOPE_0] - data_frame.loc[i, COL_EIGEN_SLOPE_1], 2)
            data_frame.loc[i, COL_DAILY_LIMIT_COUNT] = api.daily_limit_up_count(daily=daily, begin=0, end=GAP * 2)
        except Exception as e:
            print('excetion in {}'.format(i))
            continue
        print('##### {i} #####'.format(i=i))
        time.sleep(0.1)

    data_frame = data_frame[
                           (data_frame[COL_EIGEN_SLOPE_0] > 0)
                           & (data_frame[COL_EIGEN_SLOPE_1] > 0)                           # & (data_frame[COL_DAILY_LIMIT_COUNT] == 0)
                           # & (data_frame[COL_ACCUMULATE_P_CHANGE] > 5)
                           # & (data_frame[COL_PRE_ACCUMULATE_P_CHANGE] < data_frame[COL_ACCUMULATE_P_CHANGE])
                           ]

    sorted_frame = data_frame.sort_values(by=COL_EIGEN_SLOPE_DIFF, ascending=False)

    file_name = '../logs/{date}@EigenSlope.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)


if __name__ == '__main__':
    main()