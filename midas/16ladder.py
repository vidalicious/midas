# -*- coding: utf-8 -*-
import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.api as api

__version__ = 16

COL_P_CHANGE_RANGE = 'p_change_range'
DAY_RANGE = (0, 1)
COL_STOPMARK = 'stop_mark'

# 上证指数
LAST_MARKET_DATE = ts.get_hist_data('000001').index[0]


def _main():
    basics = ts.get_stock_basics()

    frame = DataFrame()
    frame['name'] = basics['name']
    frame['outstanding'] = basics['outstanding']
    frame[COL_P_CHANGE_RANGE] = np.nan
    frame[COL_STOPMARK] = ''

    for i, code in enumerate(basics.index):
        if code.startswith('300'):
            continue

        hist_data = ts.get_hist_data(code)
        try:
            frame.loc[code, COL_P_CHANGE_RANGE] = api.hist_p_change(hist_data, begin=DAY_RANGE[0], end=DAY_RANGE[1])

            if hist_data.index[0] != LAST_MARKET_DATE:
                frame.loc[code, COL_STOPMARK] = 'stop'
        except Exception:
            print('excetion in {}'.format(i))
            continue

        print('#####', i, '#####')

    # observe
    filtered_frame = frame[
                           (frame[COL_P_CHANGE_RANGE] > 9.8)
                           & (frame[COL_STOPMARK] != 'stop')
                            ]

    sorted_frame = filtered_frame.sort_values(by=COL_P_CHANGE_RANGE, ascending=False)
    print(sorted_frame)

    file_name = '../logs/{date}@observer.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)


if __name__ == '__main__':
    _main()
