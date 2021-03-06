# -*- coding: utf-8 -*-
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.legacy.api_pro as api

COL_CONTINUOUSLY_LIMIT_UP = 'continuously_limit_up'
COL_CONTINUOUSLY_UP = 'continuously_up'
COL_AVERAGE_P_CHANGE = 'average_p_change'
COL_LAST_P_CHANGE = 'last_p_change'

sampling_count = 100


def main():
    pro = ts.pro_api()

    trade_dates = pro.daily(ts_code='000001.SZ').trade_date
    LAST_MARKET_DATE = trade_dates[0]

    stock_basic = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,industry,fullname')

    data_frame = DataFrame()
    for key in ['ts_code', 'name', 'industry']:
        data_frame[key] = stock_basic[key]

    for key in [COL_CONTINUOUSLY_LIMIT_UP, COL_CONTINUOUSLY_UP, COL_AVERAGE_P_CHANGE, COL_LAST_P_CHANGE, 'circ_mv']:
        data_frame[key] = np.nan

    for i, ts_code in enumerate(data_frame.ts_code):
        try:
            daily_basic = pro.daily_basic(ts_code=ts_code,          #trade_date=LAST_MARKET_DATE
                                          start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
            for key in ['circ_mv', ]:
                data_frame.loc[i, key] = daily_basic.loc[0, key]

            daily = pro.daily(ts_code=ts_code, start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
            continuous_up = api.daily_continuously_close_up_count(daily=daily)
            data_frame.loc[i, COL_CONTINUOUSLY_LIMIT_UP] = api.daily_continuously_limit_up_count(daily=daily)
            data_frame.loc[i, COL_CONTINUOUSLY_UP] = continuous_up
            data_frame.loc[i, COL_AVERAGE_P_CHANGE] = api.daily_average_p_change(daily=daily, begin=0, end=continuous_up)
            data_frame.loc[i, COL_LAST_P_CHANGE] = daily.pct_chg[0]
        except Exception as e:
            print('excetion in {}'.format(i))
            continue
        print('##### {i} #####'.format(i=i))
        time.sleep(0.1)

    data_frame = data_frame[
                           # (data_frame['circ_mv'] < 1000000)
                           # & (data_frame[COL_CONTINUOUSLY_UP] > 1)
                           (data_frame[COL_LAST_P_CHANGE] > 9.8)
                           ]

    sorted_frame = data_frame.sort_values(by=COL_CONTINUOUSLY_LIMIT_UP, ascending=False)

    file_name = '../logs/{date}@HeavyChaser.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)


if __name__ == '__main__':
    main()
