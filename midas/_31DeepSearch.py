# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.api_pro as api

COL_DEEP_INDEX = 'COL_DEEP_INDEX'
COL_FALL_P_CHANGE = 'COL_FALL_P_CHANGE'
COL_CURRENT_PRICE = 'COL_CURRENT_PRICE'
COL_INDAY_P_CHANGE = 'COL_INDAY_P_CHANGE'

sampling_count = 100


def main():
    pro = ts.pro_api()

    trade_dates = pro.daily(ts_code='000001.SZ').trade_date
    LAST_MARKET_DATE = trade_dates[0]

    stock_basic = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,industry,fullname')

    data_frame = DataFrame()
    for key in ['ts_code', 'name', 'industry']:
        data_frame[key] = stock_basic[key]

    for key in [COL_DEEP_INDEX, COL_FALL_P_CHANGE, COL_CURRENT_PRICE, COL_INDAY_P_CHANGE, 'circ_mv']:
        data_frame[key] = np.nan

    for i, ts_code in enumerate(data_frame.ts_code):
        try:
            daily_basic = pro.daily_basic(ts_code=ts_code,          #trade_date=LAST_MARKET_DATE
                                          start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
            for key in ['circ_mv', ]:
                data_frame.loc[i, key] = daily_basic.loc[0, key]

            daily = pro.daily(ts_code=ts_code, start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
            index = api.daily_weight_lowest_index(daily=daily, begin=0, end=2)
            data_frame.loc[i, COL_DEEP_INDEX] = index
            data_frame.loc[i, COL_FALL_P_CHANGE] = api.daily_weight_free_continuously_fall_p_change(daily=daily, begin=index)
            data_frame.loc[i, COL_CURRENT_PRICE] = daily.close[0]
            data_frame.loc[i, COL_INDAY_P_CHANGE] = api.daily_inday_p_change(daily=daily, index=0)
        except Exception as e:
            print('excetion in {}'.format(i))
            continue
        print('##### {i} #####'.format(i=i))
        time.sleep(0.1)

    data_frame = data_frame[
                           (data_frame[COL_FALL_P_CHANGE] < 0)
                           & (data_frame[COL_INDAY_P_CHANGE] > 0)
                           # & (data_frame[COL_ACCUMULATE_P_CHANGE] > 5)
                           # & (data_frame[COL_PRE_ACCUMULATE_P_CHANGE] < data_frame[COL_ACCUMULATE_P_CHANGE])
                           ]

    sorted_frame = data_frame.sort_values(by=COL_FALL_P_CHANGE, ascending=True)

    file_name = '../logs/{date}@DeepSearch.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)


if __name__ == '__main__':
    main()