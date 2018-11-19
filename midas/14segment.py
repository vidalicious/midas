# -*- coding: utf-8 -*-
import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.api as api

__version__ = 13

COL_P_CHANGE_RANGE = 'p_change_range'
COL_P_CHANGE_TILL_NOW = 'p_change_till_now'
COL_NORMALIZING_STD = 'normalizing_std'
COL_NORMALIZING_STD_TILL_NOW = 'normalizing_std_till_now'
DELTA_RANGE = (0, 15)
PERIOD = 20
COL_STOPMARK = 'stop_mark'
N = 5


# 上证指数
LAST_MARKET_DATE = ts.get_hist_data('000001').index[0]


def _main():
    basics = ts.get_stock_basics()

    frames = list()

    for i in range(0, N):
        frame = DataFrame()
        frame['name'] = basics['name']
        frame['outstanding'] = basics['outstanding']
        frame[COL_P_CHANGE_RANGE] = np.nan
        frame[COL_NORMALIZING_STD] = np.nan
        frame[COL_P_CHANGE_TILL_NOW] = np.nan
        frame[COL_NORMALIZING_STD_TILL_NOW] = np.nan
        frame[COL_STOPMARK] = ''
        frames.append(frame)

    for i, code in enumerate(basics.index):
        if code.startswith('300'):
            continue

        hist_data = ts.get_hist_data(code)
        try:
            for j in range(0, N):
                frame = frames[j]
                frame.loc[code, COL_P_CHANGE_RANGE] = api.hist_p_change(hist_data, begin=PERIOD * j + DELTA_RANGE[0], end=PERIOD * j + DELTA_RANGE[1])
                frame.loc[code, COL_NORMALIZING_STD] = api.normalizing_std_close(hist_data, begin=PERIOD * j + DELTA_RANGE[0], end=PERIOD * j + DELTA_RANGE[1])
                frame.loc[code, COL_P_CHANGE_TILL_NOW] = api.hist_p_change(hist_data, begin=0, end=PERIOD * j + DELTA_RANGE[0])
                frame.loc[code, COL_NORMALIZING_STD_TILL_NOW] = api.normalizing_std_close(hist_data, begin=0, end=PERIOD * j + DELTA_RANGE[0])

                if hist_data.index[0] != LAST_MARKET_DATE:
                    frame.loc[code, COL_STOPMARK] = 'stop'

        except Exception:
            print('excetion in {}'.format(i))
            continue

        print('#####', i, '#####')

    for i in range(0, N):
        frame = frames[i]

        # observe
        filtered_frame = frame[
                               (frame[COL_P_CHANGE_RANGE] < -15)
                               & (frame['outstanding'] < 10)
                               & (frame[COL_STOPMARK] != 'stop')
                                ]

        sorted_frame = filtered_frame.sort_values(by=COL_P_CHANGE_RANGE)
        print(sorted_frame)

        file_name = '../logs/{date}@segment_period_{i}.csv'.format(date=LAST_MARKET_DATE, i=i)
        # print(fileName)
        with open(file_name, 'w') as file:
            sorted_frame.to_csv(file)


if __name__ == '__main__':
    _main()
