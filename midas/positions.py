# -*- coding: utf-8 -*-
import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.const as const
import midas.midas.api as api

COL_CLOSE = 'close'
COL_UPPERLIMIT = 'upper_limit'
COL_LOWERLIMIT = 'lower_limit'

K_UPPER_LIMIT_RATIO = 3

# 上证指数
LAST_MARKET_DATE = ts.get_hist_data('000001').index[0]


def _main():
    basics = ts.get_stock_basics()

    frame = DataFrame()
    frame['name'] = np.nan
    # frame['pe'] = basics['pe']
    frame['close'] = np.nan
    frame[COL_UPPERLIMIT] = np.nan
    frame[COL_LOWERLIMIT] = np.nan

    for i, code in enumerate(const.positions):
        frame.loc[code, 'name'] = basics.loc[code, 'name']
        hist_data = ts.get_hist_data(code)
        try:
            frame.loc[code, COL_CLOSE] = hist_data['close'][0]
            frame.loc[code, COL_UPPERLIMIT] = api.next_close_to_tunnel_top(hist_data, n=5, ratio=K_UPPER_LIMIT_RATIO)
            frame.loc[code, COL_LOWERLIMIT] = api.next_close_to_ma(hist_data, n=5)
        except Exception:
            continue

        print('#####', i, '#####')

    file_name = '../logs/{date}@Positions.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        frame.to_csv(file)


if __name__ == '__main__':
    _main()
