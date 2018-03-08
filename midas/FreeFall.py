# -*- coding: utf-8 -*-
import tushare as ts
from pandas import DataFrame
import numpy as np

from midas.midas.api import hist_p_change as hpc
from midas.midas.api import past_average_turnover as pat

__version__ = 4

COL_PAST_P_CHANGE = 'past_p_change'
COL_PASTAVERAGETURNOVER = 'past_average_turnover'
COL_STOPMARK = 'stop_mark'
DAY_BEGIN = 0
DAY_END = 10
PAST_AVERAGE_TURNOVER_PERIOD = 3

# 上证指数
LAST_MARKET_DATE = ts.get_hist_data('000001').index[0]

def _main():
    basics = ts.get_stock_basics()

    frame = DataFrame()
    frame['name'] = basics['name']
    frame['pe'] = basics['pe']
    frame[COL_PAST_P_CHANGE] = np.nan
    frame[COL_PASTAVERAGETURNOVER] = np.nan
    frame[COL_STOPMARK] = np.nan
    i = 0
    for code in basics.index:
        hist_data = ts.get_hist_data(code)
        try:
            frame.loc[code, COL_PAST_P_CHANGE] = hpc(hist_data, begin=DAY_BEGIN, end=DAY_END)
            frame.loc[code, COL_PASTAVERAGETURNOVER] = pat(hist_data, PAST_AVERAGE_TURNOVER_PERIOD)
            if hist_data.index[0] != LAST_MARKET_DATE:
                frame.loc[code, COL_STOPMARK] = 'stop'
        except Exception:
            continue

        i += 1
        print('#####', i, '#####')

    filtered_frame = frame[(frame[COL_PAST_P_CHANGE] < 0)
                           & (frame[COL_PASTAVERAGETURNOVER] < 20) & (frame[COL_PASTAVERAGETURNOVER] > 0.5)
                           & (frame['pe'] < 100) & (frame['pe'] > 0)
                           & (frame[COL_STOPMARK] != 'stop')]

    sorted_frame = filtered_frame.sort_values(by=COL_PAST_P_CHANGE)
    print(sorted_frame)

    file_name = '../logs/%s@FreeFall%s' % (LAST_MARKET_DATE, '.csv')
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)


if __name__ == '__main__':
    _main()
