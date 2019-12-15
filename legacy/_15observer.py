# -*- coding: utf-8 -*-
import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.legacy.api as api

__version__ = 15

COL_P_CHANGE_RANGE0 = 'p_change_range0'
COL_P_CHANGE_RANGE1 = 'p_change_range1'
COL_NORMALIZING_STD1 = 'normalizing_std1'
COL_OUTSTANDING = 'outstanding'
COL_MARKET_VALUE = 'market_value'
COL_STOPMARK = 'stop_mark'
DAY_RANGE0 = (0, 1)
DAY_RANGE1 = (0, 3)

PAST_AVERAGE_TURNOVER_PERIOD = 3

# 上证指数
LAST_MARKET_DATE = ts.get_hist_data('000001').index[0]


def _main():
    basics = ts.get_stock_basics()

    frame = DataFrame()
    frame['name'] = basics['name']
    frame[COL_OUTSTANDING] = basics[COL_OUTSTANDING]
    frame[COL_MARKET_VALUE] = np.nan
    frame[COL_P_CHANGE_RANGE0] = np.nan
    frame[COL_P_CHANGE_RANGE1] = np.nan
    frame[COL_NORMALIZING_STD1] = np.nan
    frame[COL_STOPMARK] = ''

    for i, code in enumerate(basics.index):
        if code.startswith('300'):
            continue

        hist_data = ts.get_hist_data(code)
        try:
            frame.loc[code, COL_MARKET_VALUE] = round(frame.loc[code, COL_OUTSTANDING] * hist_data['close'][0], 1)
            frame.loc[code, COL_P_CHANGE_RANGE0] = api.hist_p_change(hist_data, begin=DAY_RANGE0[0], end=DAY_RANGE0[1])
            frame.loc[code, COL_P_CHANGE_RANGE1] = api.hist_p_change(hist_data, begin=DAY_RANGE1[0], end=DAY_RANGE1[1])
            frame.loc[code, COL_NORMALIZING_STD1] = api.normalizing_std_close(hist_data, begin=DAY_RANGE1[0], end=DAY_RANGE1[1])

            if hist_data.index[0] != LAST_MARKET_DATE:
                frame.loc[code, COL_STOPMARK] = 'stop'
        except Exception:
            print('excetion in {}'.format(i))
            continue

        print('#####', i, '#####')

    # observe
    filtered_frame = frame[
                           # (frame[COL_P_CHANGE_RANGE0] < 0)
                           # & (frame[COL_P_CHANGE_RANGE1] > 0)
                           # & (frame[COL_NORMALIZING_STD] < 0.03)
                            (frame[COL_MARKET_VALUE] < 100)
                           & (frame[COL_STOPMARK] != 'stop')
                            ]

    sorted_frame = filtered_frame.sort_values(by=COL_P_CHANGE_RANGE1, ascending=False)
    print(sorted_frame)

    file_name = '../logs/{date}@observer.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)


if __name__ == '__main__':
    _main()
