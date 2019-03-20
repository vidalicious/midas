# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.api_pro as api

COL_WEIGHT_RISE_EFFICIENCY = 'COL_WEIGHT_RISE_EFFICIENCY'
COL_WEIGHT_MIN_INDEX = 'COL_WEIGHT_MIN_INDEX'
COL_WEIGHT_MAX_INDEX = 'COL_WEIGHT_MAX_INDEX'
COL_CURRENT_PRICE = 'COL_CURRENT_PRICE'

sampling_count = 100


def main():
    pro = ts.pro_api()

    trade_dates = pro.daily(ts_code='000001.SZ').trade_date
    LAST_MARKET_DATE = trade_dates[0]

    stock_basic = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,industry,fullname')

    data_frame = DataFrame()
    for key in ['ts_code', 'name', 'industry']:
        data_frame[key] = stock_basic[key]

    for key in [COL_WEIGHT_RISE_EFFICIENCY, COL_WEIGHT_MIN_INDEX, COL_WEIGHT_MAX_INDEX, COL_CURRENT_PRICE, 'circ_mv']:
        data_frame[key] = np.nan

    for i, ts_code in enumerate(data_frame.ts_code):
        status = 0
        retry = 5
        while status != 2 and retry > 0:
            retry = retry - 1
            try:
                daily_basic = pro.daily_basic(ts_code=ts_code,  # trade_date=LAST_MARKET_DATE
                                              start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
                for key in ['circ_mv', ]:
                    data_frame.loc[i, key] = daily_basic.loc[0, key]

                daily = pro.daily(ts_code=ts_code, start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
                (data_frame.loc[i, COL_WEIGHT_RISE_EFFICIENCY],
                 data_frame.loc[i, COL_WEIGHT_MIN_INDEX],
                 data_frame.loc[i, COL_WEIGHT_MAX_INDEX]) = api.daily_weight_rise_efficiency(daily=daily, begin=0,
                                                                                             end=30)
                data_frame.loc[i, COL_CURRENT_PRICE] = daily.close[0]
                print('##### {i} #####'.format(i=i))
                time.sleep(0.1)
                status = 2
            except Exception as e:
                print('excetion in {}'.format(i))
                status = 1
                continue


        # try:
        #     daily_basic = pro.daily_basic(ts_code=ts_code,          #trade_date=LAST_MARKET_DATE
        #                                   start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
        #     for key in ['circ_mv', ]:
        #         data_frame.loc[i, key] = daily_basic.loc[0, key]
        #
        #     daily = pro.daily(ts_code=ts_code, start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
        #     (data_frame.loc[i, COL_WEIGHT_RISE_EFFICIENCY],
        #      data_frame.loc[i, COL_WEIGHT_MIN_INDEX],
        #      data_frame.loc[i, COL_WEIGHT_MAX_INDEX]) = api.daily_weight_rise_efficiency(daily=daily, begin=0, end=30)
        #     data_frame.loc[i, COL_CURRENT_PRICE] = daily.close[0]
        # except Exception as e:
        #     print('excetion in {}'.format(i))
        #     continue
        # print('##### {i} #####'.format(i=i))
        # time.sleep(0.1)

    dragons_frame = data_frame[
                               (data_frame[COL_WEIGHT_RISE_EFFICIENCY] > 3)
                               & data_frame[COL_WEIGHT_MAX_INDEX] < 10
                               ]
    sorted_dragons = dragons_frame.sort_values(by=COL_WEIGHT_RISE_EFFICIENCY, ascending=False)
    file_name = '../logs/{date}@RiseTempo_Dragons.csv'.format(date=LAST_MARKET_DATE)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_dragons.to_csv(file)

    dandelion_frame = data_frame[
        data_frame[COL_WEIGHT_MAX_INDEX] == 0
    ]

    sorted_dandelion = dandelion_frame.sort_values(by=COL_WEIGHT_MIN_INDEX, ascending=True)
    file_name = '../logs/{date}@RiseTempo_Dandelion.csv'.format(date=LAST_MARKET_DATE)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_dandelion.to_csv(file)

    # data_frame = data_frame[
    #                        (data_frame[COL_WEIGHT_RISE_EFFICIENCY] > 0)
    #                        & ((data_frame[COL_WEIGHT_MAX_INDEX] == 0) | ((data_frame[COL_WEIGHT_RISE_EFFICIENCY] > 3) & (data_frame[COL_WEIGHT_MAX_INDEX] < 5)))
    #                        # & (data_frame[COL_ACCUMULATE_P_CHANGE] > 5)
    #                        # & (data_frame[COL_PRE_ACCUMULATE_P_CHANGE] < data_frame[COL_ACCUMULATE_P_CHANGE])
    #                        ]
    #
    # sorted_frame = data_frame.sort_values(by=COL_WEIGHT_RISE_EFFICIENCY, ascending=False)
    #
    # file_name = '../logs/{date}@RiseTempo.csv'.format(date=LAST_MARKET_DATE)
    # # print(fileName)
    # with open(file_name, 'w', encoding='utf8') as file:
    #     sorted_frame.to_csv(file)


if __name__ == '__main__':
    main()