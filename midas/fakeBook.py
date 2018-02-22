# -*- coding: utf-8 -*-
import tushare as ts
import time
from functools import reduce
from pandas import DataFrame

COL_PASTCHANGE = 'past_p_change'
COL_PASTPOSITIVE = 'past_positive'
PAST_DAY_PERIOD = 10
PAST_POSITIVE_PERIOD = 2


def past_hist_p_change(histData, pastDay=5):
    past_p_changes = histData['p_change'][:pastDay]
    mul = reduce(lambda x, y: x*y, map(lambda x: 1+x/100, past_p_changes.values))
    return (mul - 1) * 100


def _main():
    names = ts.get_stock_basics()['name']

    frame = DataFrame()
    frame['name'] = names
    frame[COL_PASTCHANGE] = None
    frame[COL_PASTPOSITIVE] = None
    i = 0
    for code in names.index:
        histData = ts.get_hist_data(code)
        try:
            frame[COL_PASTCHANGE][code] = past_hist_p_change(histData, PAST_DAY_PERIOD)
            if past_hist_p_change(histData, PAST_POSITIVE_PERIOD) > 0:
                frame[COL_PASTPOSITIVE][code] = '★'
        except Exception:
            continue

        i += 1
        print('#####', i, '#####')

    sortedFrame = frame.sort_values(by=COL_PASTCHANGE)
    print(sortedFrame)

    t = time.strftime('%Y-%m-%d', time.localtime())
    fileName = '../logs/%s%s' %(t, '.csv')
    # print(fileName)
    with open(fileName, 'w', encoding='utf8') as file:
        sortedFrame.to_csv(file)


if __name__=='__main__':
    _main()