# -*- coding: utf-8 -*-
import tushare as ts
import time
from functools import reduce
from pandas import DataFrame
import numpy as np

__version__ = 1

COL_PASTCHANGE = 'past_p_change'
COL_PASTPOSITIVE = 'past_positive'
PAST_DAY_PERIOD = 10
PAST_POSITIVE_PERIOD = 2


def past_hist_p_change(histData, pastDay=5):
    past_p_changes = histData['p_change'][:pastDay]
    mul = reduce(lambda x, y: x*y, map(lambda x: 1+x/100, past_p_changes.values))
    return round((mul - 1) * 100, 3)


def _main():
    basics = ts.get_stock_basics()

    frame = DataFrame()
    frame['name'] = basics['name']
    frame[COL_PASTCHANGE] = np.nan
    frame[COL_PASTPOSITIVE] = np.nan
    frame['pe'] = basics['pe']
    i = 0
    for code in basics.index:
        histData = ts.get_hist_data(code)
        try:
            frame.loc[code, COL_PASTCHANGE] = past_hist_p_change(histData, PAST_DAY_PERIOD)
            if past_hist_p_change(histData, PAST_POSITIVE_PERIOD) > 0:
                frame.loc[code, COL_PASTPOSITIVE] = '★'
        except Exception:
            continue

        i += 1
        print('#####', i, '#####')

    sortedFrame = frame.sort_values(by=COL_PASTCHANGE)
    print(sortedFrame)

    t = time.strftime('%Y-%m-%d', time.localtime())
    fileName = '../logs/%s@fakeBook%s' %(t, '.csv')
    # print(fileName)
    with open(fileName, 'w', encoding='utf8') as file:
        sortedFrame.to_csv(file)


if __name__=='__main__':
    _main()