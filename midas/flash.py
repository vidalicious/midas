# -*- coding: utf-8 -*-
import tushare as ts
import time
from pandas import DataFrame
import numpy as np

from midas.midas.api import hist_p_change as hpc
from midas.midas.api import past_average_turnover as pat


COL_PASTFAR = 'past_far'
COL_PASTNEAR = 'past_near'
COL_PASTAVERAGETURNOVER = 'past_average_turnover'
DAY_NEAR = 2
DAY_FAR = 12
PAST_AVERAGE_TURNOVER_PERIOD = 3


def _main():
    basics = ts.get_stock_basics()

    frame = DataFrame()
    frame['name'] = basics['name']
    frame['pe'] = basics['pe']
    frame[COL_PASTFAR] = np.nan
    frame[COL_PASTNEAR] = np.nan
    frame[COL_PASTAVERAGETURNOVER] = np.nan
    i = 0
    for code in basics.index:
        hist_data = ts.get_hist_data(code)
        try:
            frame.loc[code, COL_PASTFAR] = hpc(hist_data, begin=DAY_NEAR, end=DAY_FAR)
            frame.loc[code, COL_PASTNEAR] = hpc(hist_data, begin=0, end=DAY_NEAR)
            frame.loc[code, COL_PASTAVERAGETURNOVER] = pat(hist_data, PAST_AVERAGE_TURNOVER_PERIOD)
        except Exception:
            continue

        i += 1
        print('#####', i, '#####')

    filtered_frame = frame[(frame[COL_PASTFAR] < 0)
                           & (frame[COL_PASTNEAR] > 0)
                           & (frame[COL_PASTAVERAGETURNOVER] < 10) & (frame[COL_PASTAVERAGETURNOVER] > 0.5)
                           & (frame['pe'] < 100) & (frame['pe'] > 0)]

    sorted_frame = filtered_frame.sort_values(by=COL_PASTFAR)
    print(sorted_frame)

    t = time.strftime('%Y-%m-%d', time.localtime())
    file_name = '../logs/%s@flash%s' % (t, '.csv')
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)


if __name__ == '__main__':
    _main()
