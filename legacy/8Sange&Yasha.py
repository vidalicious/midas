# -*- coding: utf-8 -*-
import tushare as ts
from pandas import DataFrame
import numpy as np

from midas.legacy.api import hist_p_change as hpc
from midas.legacy.api import past_average_turnover as pat
from midas.legacy.api import is_cross_ma5_ma10 as ic510

__version__ = 8

COL_P_CHANGE_01 = 'p_change_01'
COL_PASTAVERAGETURNOVER = 'past_average_turnover'
COL_STOPMARK = 'stop_mark'
COL_ISCROSS = 'is_cross'

DAY_0 = 0
DAY_1 = 15
PAST_AVERAGE_TURNOVER_PERIOD = 3

# 上证指数
LAST_MARKET_DATE = ts.get_hist_data('000001').index[0]


def _main():
    basics = ts.get_stock_basics()

    frame = DataFrame()
    frame['name'] = basics['name']
    frame['pe'] = basics['pe']
    frame[COL_P_CHANGE_01] = np.nan
    frame[COL_PASTAVERAGETURNOVER] = np.nan
    frame[COL_STOPMARK] = np.nan
    frame[COL_ISCROSS] = np.nan

    for i, code in enumerate(basics.index):
        hist_data = ts.get_hist_data(code)
        try:
            frame.loc[code, COL_P_CHANGE_01] = hpc(hist_data, begin=DAY_0, end=DAY_1)
            frame.loc[code, COL_PASTAVERAGETURNOVER] = pat(hist_data, PAST_AVERAGE_TURNOVER_PERIOD)
            if hist_data.index[0] != LAST_MARKET_DATE:
                frame.loc[code, COL_STOPMARK] = 'stop'
            frame.loc[code, COL_ISCROSS] = ic510(hist_data)
        except Exception:
            continue

        print('#####', i, '#####')

    filtered_frame = frame[(frame[COL_STOPMARK] != 'stop')
                           & (frame[COL_ISCROSS] is True)]

    sorted_frame = filtered_frame.sort_values(by=COL_P_CHANGE_01)
    print(sorted_frame)

    file_name = '../logs/{date}@Sange&Yasha.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)


if __name__ == '__main__':
    _main()
