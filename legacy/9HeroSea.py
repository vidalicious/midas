# -*- coding: utf-8 -*-
import tushare as ts
from pandas import DataFrame
import numpy as np

from midas.legacy.api import hist_p_change as hpc
from midas.legacy.api import past_average_turnover as pat
from midas.legacy.const import leading_shares

__version__ = 9

COL_P_CHANGE_01 = 'p_change_01'
COL_PASTAVERAGETURNOVER = 'past_average_turnover'
COL_STOPMARK = 'stop_mark'
DAY_0 = 0
DAY_1 = 20
PAST_AVERAGE_TURNOVER_PERIOD = 3

# 上证指数
LAST_MARKET_DATE = ts.get_hist_data('000001').index[0]


def _main():
    basics = ts.get_stock_basics()

    frame = DataFrame()
    frame['name'] = np.nan
    # frame['pe'] = basics['pe']
    frame[COL_P_CHANGE_01] = np.nan
    frame[COL_PASTAVERAGETURNOVER] = np.nan
    frame[COL_STOPMARK] = ''

    for i, code in enumerate(leading_shares):
        frame.loc[code, 'name'] = basics.loc[code, 'name']
        hist_data = ts.get_hist_data(code)
        try:
            frame.loc[code, COL_P_CHANGE_01] = hpc(hist_data, begin=DAY_0, end=DAY_1)
            frame.loc[code, COL_PASTAVERAGETURNOVER] = pat(hist_data, PAST_AVERAGE_TURNOVER_PERIOD)
            if hist_data.index[0] != LAST_MARKET_DATE:
                frame.loc[code, COL_STOPMARK] = 'stop'
        except Exception:
            continue

        print('#####', i, '#####')

    filtered_frame = frame[(frame[COL_STOPMARK] != 'stop')]

    sorted_frame = filtered_frame.sort_values(by=COL_P_CHANGE_01)
    print(sorted_frame)

    file_name = '../logs/{date}@HeroSea.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)


if __name__ == '__main__':
    _main()
