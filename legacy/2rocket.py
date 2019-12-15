# -*- coding: utf-8 -*-
import tushare as ts
import time
from pandas import DataFrame
import numpy as np

from midas.legacy.api import past_hist_p_change as phpc
from midas.legacy.api import past_average_turnover as pat

__version__ = 2

COL_PASTCHANGE = 'past_p_change'
COL_PASTPOSITIVE = 'past_positive'
COL_PASTAVERAGETURNOVER = 'past_average_turnover'
PAST_DAY_PERIOD = 10
PAST_POSITIVE_PERIOD = 2
PAST_AVERAGE_TURNOVER_PERIOD = 3


def _main():
    basics = ts.get_stock_basics()

    frame = DataFrame()
    frame['name'] = basics['name']
    frame[COL_PASTCHANGE] = np.nan
    frame[COL_PASTPOSITIVE] = np.nan
    frame['pe'] = basics['pe']
    i = 0
    for code in basics.index:
        hist_data = ts.get_hist_data(code)
        try:
            frame.loc[code, COL_PASTCHANGE] = phpc(hist_data, PAST_DAY_PERIOD)
            if phpc(hist_data, PAST_POSITIVE_PERIOD) > 0:
                frame.loc[code, COL_PASTPOSITIVE] = '★'
            frame.loc[code, COL_PASTAVERAGETURNOVER] = pat(hist_data, PAST_AVERAGE_TURNOVER_PERIOD)
        except Exception:
            continue

        i += 1
        print('#####', i, '#####')

    sorted_frame = frame.sort_values(by=COL_PASTCHANGE)
    print(sorted_frame)

    t = time.strftime('%Y-%m-%d', time.localtime())
    file_name = '../logs/%s@rocket%s' % (t, '.csv')
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)


if __name__ == '__main__':
    _main()
