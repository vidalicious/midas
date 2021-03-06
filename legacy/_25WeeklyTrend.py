# -*- coding: utf-8 -*-
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.legacy.api_pro as api

COL_CONTINUOUSLY_UP = 'continuously_up'
COL_AVERAGE_TURNOVER = 'average_turnover_rate'
COL_LAST_5DAY_WEIGHT_P_CHANGE = 'LAST_5DAY_WEIGHT_P_CHANGE'
COL_LAST_DAY_P_CHANGE = 'LAST_DAY_P_CHANGE'


sampling_count = 300
period = 5

def main():
    pro = ts.pro_api()

    trade_dates = pro.daily(ts_code='000001.SZ').trade_date
    LAST_MARKET_DATE = trade_dates[0]

    stock_basic = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,industry,fullname')

    data_frame = DataFrame()
    for key in ['ts_code', 'name', 'industry']:
        data_frame[key] = stock_basic[key]

    for key in [COL_CONTINUOUSLY_UP, COL_AVERAGE_TURNOVER, COL_LAST_5DAY_WEIGHT_P_CHANGE, COL_LAST_DAY_P_CHANGE]:
        data_frame[key] = np.nan

    for i, ts_code in enumerate(data_frame.ts_code):
        try:
            weekly = pro.weekly(ts_code=ts_code,          #trade_date=LAST_MARKET_DATE
                                     start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)

            continuous_up = api.weekly_continuously_weight_up_count(weekly=weekly)
            data_frame.loc[i, COL_CONTINUOUSLY_UP] = continuous_up

            daily_basic = pro.daily_basic(ts_code=ts_code,  # trade_date=LAST_MARKET_DATE
                                          start_date=trade_dates[10], end_date=LAST_MARKET_DATE)
            data_frame.loc[i, COL_AVERAGE_TURNOVER] = api.daily_basic_average_turnover_rate(daily_basic=daily_basic, begin=0, end=2)

            daily = pro.daily(ts_code=ts_code, start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
            weight_0 = api.daily_period_weight(daily=daily, begin=0, end=period)
            weight_1 = api.daily_period_weight(daily=daily, begin=period, end=2 * period)

            data_frame.loc[i, COL_LAST_5DAY_WEIGHT_P_CHANGE] = round(((weight_0 / weight_1) - 1) * 100, 2)
            data_frame.loc[i, COL_LAST_DAY_P_CHANGE] = api.daily_accumulate_p_change(daily=daily, begin=0, end=1)
        except Exception as e:
            print('excetion in {}'.format(i))
            continue
        print('##### {i} #####'.format(i=i))
        time.sleep(0.1)

    data_frame = data_frame[
                           # (data_frame['circ_mv'] < 1000000)
                           # & (data_frame[COL_CONTINUOUSLY_UP] > 1)
                           (data_frame[COL_LAST_5DAY_WEIGHT_P_CHANGE] > 10)
                           | (data_frame[COL_LAST_DAY_P_CHANGE] > 9.8)
                           ]

    sorted_frame = data_frame.sort_values(by=COL_LAST_5DAY_WEIGHT_P_CHANGE, ascending=False)

    file_name = '../logs/{date}@WeeklyTrend.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)


if __name__ == '__main__':
    main()
