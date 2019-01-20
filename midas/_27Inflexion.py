# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.api_pro as api

COL_WEIGHT_CONTINUOUSLY_FALL_P_CHANGE = 'WEIGHT_CONTINUOUSLY_FALL_P_CHANGE'
COL_INDAY_P_CHANGE = 'INDAY_P_CHANGE'
COL_WEEKLY_CONTINUOUSLY_UP_COUNT = 'WEEKLY_CONTINUOUSLY_UP_COUNT'

sampling_count = 100


def main():
    pro = ts.pro_api()

    trade_dates = pro.daily(ts_code='000001.SZ').trade_date
    LAST_MARKET_DATE = trade_dates[1]

    stock_basic = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,industry,fullname')

    data_frame = DataFrame()
    for key in ['ts_code', 'name', 'industry']:
        data_frame[key] = stock_basic[key]

    for key in [COL_WEIGHT_CONTINUOUSLY_FALL_P_CHANGE, COL_INDAY_P_CHANGE,
                COL_WEEKLY_CONTINUOUSLY_UP_COUNT]:
        data_frame[key] = np.nan

    for i, ts_code in enumerate(data_frame.ts_code):
        try:
            daily = pro.daily(ts_code=ts_code, start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
            data_frame.loc[i, COL_WEIGHT_CONTINUOUSLY_FALL_P_CHANGE] = api.daily_weight_continuously_fall_p_change(daily=daily, begin=1)
            data_frame.loc[i, COL_INDAY_P_CHANGE] = api.daily_inday_p_change(daily=daily, index=0)
            weekly = pro.weekly(ts_code=ts_code,          #trade_date=LAST_MARKET_DATE
                                start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
            data_frame.loc[i, COL_WEEKLY_CONTINUOUSLY_UP_COUNT] = api.weekly_continuously_weight_up_count(weekly=weekly)
        except Exception as e:
            print('excetion in {}'.format(i))
            continue
        print('##### {i} #####'.format(i=i))
        time.sleep(0.1)

    data_frame = data_frame[
                           # (data_frame['circ_mv'] < 1000000)
                           (data_frame[COL_WEIGHT_CONTINUOUSLY_FALL_P_CHANGE] < 0)
                           & (data_frame[COL_INDAY_P_CHANGE] > 0)
                           ]

    sorted_frame = data_frame.sort_values(by=COL_WEEKLY_CONTINUOUSLY_UP_COUNT, ascending=False)

    file_name = '../logs/{date}@Inflexion.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)


if __name__ == '__main__':
    main()
