# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.api_pro as api

COL_CONTINUOUSLY_UP = 'continuously_up'
COL_AVERAGE_P_CHANGE = 'average_p_change'

sampling_count = 300


def main():
    pro = ts.pro_api()

    trade_dates = pro.daily(ts_code='000001.SZ').trade_date
    LAST_MARKET_DATE = trade_dates[0]

    stock_basic = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,industry,fullname')

    data_frame = DataFrame()
    for key in ['ts_code', 'name', 'industry']:
        data_frame[key] = stock_basic[key]

    for key in [COL_CONTINUOUSLY_UP, COL_AVERAGE_P_CHANGE]:
        data_frame[key] = np.nan

    for i, ts_code in enumerate(data_frame.ts_code):
        try:
            weekly = pro.weekly(ts_code=ts_code,          #trade_date=LAST_MARKET_DATE
                                     start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)

            continuous_up = api.weekly_continuously_low_up_count(weekly=weekly)
            data_frame.loc[i, COL_CONTINUOUSLY_UP] = continuous_up
            data_frame.loc[i, COL_AVERAGE_P_CHANGE] = api.weekly_average_p_change(weekly=weekly, begin=0, end=continuous_up)
        except Exception as e:
            print('excetion in {}'.format(i))
            continue
        print('##### {i} #####'.format(i=i))
        time.sleep(0.1)

    data_frame = data_frame[
                           # (data_frame['circ_mv'] < 1000000)
                           # & (data_frame[COL_CONTINUOUSLY_UP] > 1)
                           (data_frame[COL_CONTINUOUSLY_UP] > 2)
                           ]

    sorted_frame = data_frame.sort_values(by=COL_AVERAGE_P_CHANGE, ascending=False)

    file_name = '../logs/{date}@WeeklyTrend.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)


if __name__ == '__main__':
    main()
