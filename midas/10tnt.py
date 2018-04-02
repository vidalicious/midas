# -*- coding: utf-8 -*-
import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.api as api

__version__ = 10

COL_P_CHANGE_01 = 'p_change_01'
COL_P_CHANGE_12 = 'p_change_02'
COL_PASTAVERAGETURNOVER = 'past_average_turnover'
COL_NORMALIZING_STD = 'normalizing_std'
COL_NEXTDAYTOMA5 = 'next_day_to_ma5'
K_UP_LIMIT_RATIO = 3  # 2~4.66
COL_STOPMARK = 'stop_mark'
DAY_0 = 0
DAY_1 = 5
DAY_2 = 20
PAST_AVERAGE_TURNOVER_PERIOD = 3

# 上证指数
LAST_MARKET_DATE = ts.get_hist_data('000001').index[0]


def _main():
    basics = ts.get_stock_basics()

    frame = DataFrame()
    frame['name'] = basics['name']
    frame[COL_P_CHANGE_01] = np.nan
    frame[COL_P_CHANGE_12] = np.nan
    frame[COL_PASTAVERAGETURNOVER] = np.nan
    frame[COL_NORMALIZING_STD] = np.nan
    frame[COL_STOPMARK] = ''

    for i, code in enumerate(basics.index):
        hist_data = ts.get_hist_data(code)
        try:
            frame.loc[code, COL_P_CHANGE_01] = api.hist_p_change(hist_data, begin=DAY_0, end=DAY_1)
            frame.loc[code, COL_P_CHANGE_12] = api.hist_p_change(hist_data, begin=DAY_1, end=DAY_2)
            frame.loc[code, COL_PASTAVERAGETURNOVER] = api.past_average_turnover(hist_data, PAST_AVERAGE_TURNOVER_PERIOD)
            frame.loc[code, COL_NORMALIZING_STD] = api.normalizing_std_close(hist_data, begin=DAY_0, end=DAY_1)
            frame.loc[code, COL_NEXTDAYTOMA5] = api.next_close_to_ma(hist_data, n=5)
            if hist_data.index[0] != LAST_MARKET_DATE:
                frame.loc[code, COL_STOPMARK] = 'stop'
        except Exception:
            print('excetion in {}'.format(i))
            continue

        print('#####', i, '#####')

    filtered_frame = frame[(frame[COL_P_CHANGE_01] > 0)
                           & (frame[COL_P_CHANGE_12] < 0)
                           # & (frame[COL_NORMALIZING_STD] < 0.03)
                           & (frame[COL_STOPMARK] != 'stop')]

    sorted_frame = filtered_frame.sort_values(by=COL_P_CHANGE_12)
    print(sorted_frame)

    file_name = '../logs/{date}@tnt.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)


if __name__ == '__main__':
    _main()
