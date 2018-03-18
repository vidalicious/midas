# -*- coding: utf-8 -*-
import tushare as ts
from pandas import DataFrame
import numpy as np

from midas.midas.api import hist_p_change as hpc
from midas.midas.api import past_average_turnover as pat

__version__ = 5

COL_P_CHANGE_01 = 'p_change_01'
COL_P_CHANGE_12 = 'p_change_12'
COL_PASTAVERAGETURNOVER = 'past_average_turnover'
COL_STOPMARK = 'stop_mark'
COL_SORT_KEY = 'sort_key'
DAY_0 = 0
DAY_1 = 10
DAY_2 = 40
PAST_AVERAGE_TURNOVER_PERIOD = 3

# 上证指数
LAST_MARKET_DATE = ts.get_hist_data('000001').index[0]


def _main():
    basics = ts.get_stock_basics()

    frame = DataFrame()
    frame['name'] = basics['name']
    frame['pe'] = basics['pe']
    frame[COL_P_CHANGE_01] = np.nan
    frame[COL_P_CHANGE_12] = np.nan
    frame[COL_PASTAVERAGETURNOVER] = np.nan
    frame[COL_STOPMARK] = np.nan
    frame[COL_SORT_KEY] = np.nan

    for i, code in enumerate(basics.index):
        hist_data = ts.get_hist_data(code)
        try:
            frame.loc[code, COL_P_CHANGE_01] = hpc(hist_data, begin=DAY_0, end=DAY_1)
            frame.loc[code, COL_P_CHANGE_12] = hpc(hist_data, begin=DAY_1, end=DAY_2)
            frame.loc[code, COL_SORT_KEY] = round(frame.loc[code, COL_P_CHANGE_01] * frame.loc[code, COL_P_CHANGE_12], 3)
            frame.loc[code, COL_PASTAVERAGETURNOVER] = pat(hist_data, PAST_AVERAGE_TURNOVER_PERIOD)
            if hist_data.index[0] != LAST_MARKET_DATE:
                frame.loc[code, COL_STOPMARK] = 'stop'
        except Exception:
            continue

        print('#####', i, '#####')

    filtered_frame = frame[(frame[COL_P_CHANGE_01] > 0)
                           & (frame[COL_P_CHANGE_12] < 0)
                           & (abs(frame[COL_P_CHANGE_12]) > abs(frame[COL_P_CHANGE_01]))
                           & (frame[COL_PASTAVERAGETURNOVER] < 20) & (frame[COL_PASTAVERAGETURNOVER] > 0.5)
                           & (frame['pe'] > 0)
                           & (frame[COL_STOPMARK] != 'stop')]

    sorted_frame = filtered_frame.sort_values(by=COL_SORT_KEY)
    print(sorted_frame)

    file_name = '../logs/{date}@EnemyChaser.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)


if __name__ == '__main__':
    _main()
