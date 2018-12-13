# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.api_pro as api

COL_AVERAGE_TURNOVER = 'average_turnover_rate'
COL_CONTINUOUSLY_UP = 'continuously_up'
COL_AVERAGE_P_CHANGE = 'average_p_change'
COL_ACCUMULATE_P_CHANGE = 'accumulate_p_change'
COL_PRE_ACCUMULATE_P_CHANGE = 'pre_accumulate_p_change'

sampling_count = 100


def main():
    pro = ts.pro_api()

    trade_dates = pro.daily(ts_code='000001.SZ').trade_date
    LAST_MARKET_DATE = trade_dates[0]

    stock_basic = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,industry,fullname')

    data_frame = DataFrame()
    for key in ['ts_code', 'name', 'industry']:
        data_frame[key] = stock_basic[key]

    for key in [COL_AVERAGE_TURNOVER, COL_CONTINUOUSLY_UP, COL_AVERAGE_P_CHANGE, COL_ACCUMULATE_P_CHANGE,
                COL_PRE_ACCUMULATE_P_CHANGE, 'circ_mv']:
        data_frame[key] = np.nan

    for i, ts_code in enumerate(data_frame.ts_code):
        if ts_code.startswith('300'):
            continue
        try:
            daily_basic = pro.daily_basic(ts_code=ts_code,          #trade_date=LAST_MARKET_DATE
                                          start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
            for key in ['circ_mv', ]:
                data_frame.loc[i, key] = daily_basic.loc[0, key]

            daily = pro.daily(ts_code=ts_code, start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
            continuous_up = api.daily_continuously_low_up_count(daily=daily)
            data_frame.loc[i, COL_CONTINUOUSLY_UP] = continuous_up
            data_frame.loc[i, COL_AVERAGE_TURNOVER] = api.daily_basic_average_turnover_rate(daily_basic=daily_basic,
                                                                                            begin=0, end=continuous_up)
            data_frame.loc[i, COL_AVERAGE_P_CHANGE] = api.daily_average_p_change(daily=daily, begin=0, end=continuous_up)
            data_frame.loc[i, COL_ACCUMULATE_P_CHANGE] = api.daily_accumulate_p_change(daily=daily, begin=0, end=continuous_up)
            data_frame.loc[i, COL_PRE_ACCUMULATE_P_CHANGE] = api.daily_accumulate_p_change(daily=daily, begin=continuous_up, end=continuous_up * 2)
        except Exception as e:
            print('excetion in {}'.format(i))
            continue
        print('##### {i} #####'.format(i=i))
        time.sleep(0.1)

    data_frame = data_frame[
                           (data_frame['circ_mv'] < 1000000)
                           & (data_frame[COL_CONTINUOUSLY_UP] > 1)
                           & (data_frame[COL_AVERAGE_TURNOVER] < 5)
                           & (data_frame[COL_ACCUMULATE_P_CHANGE] > 5)
                           & (data_frame[COL_PRE_ACCUMULATE_P_CHANGE] < data_frame[COL_ACCUMULATE_P_CHANGE])
                           ]

    industrys = dict()
    for industry in data_frame.industry:
        if industry in industrys:
            industrys[industry] = industrys[industry] + 1
        else:
            industrys[industry] = 1

    industry_frame = DataFrame()
    for i, industry in enumerate(industrys):
        industry_frame.loc[i, 'industry'] = industry
        industry_frame.loc[i, 'count'] = industrys[industry]

    sorted_frame = data_frame.sort_values(by=COL_CONTINUOUSLY_UP, ascending=False)

    file_name = '../logs/{date}@ContinuouslyUp.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)
        # for key in industrys:
        #     file.writelines('{key} {count}\n'.format(key=key, count=industrys[key]))

    file_name = '../logs/{date}@ContinuouslyUp_industry.csv'.format(date=LAST_MARKET_DATE)
    with open(file_name, 'w', encoding='utf8') as file:
        industry_frame.to_csv(file)


if __name__ == '__main__':
    main()