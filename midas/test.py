# -*- coding: utf-8 -*-
import tushare as ts
import midas.midas.api as api
import numpy as np

hist_data = ts.get_hist_data('000622')
a = api.hist_p_change(hist_data, begin=18, end=30)
b = api.normalizing_std_close(hist_data, begin=18, end=30)
print(a)
print(b)

c = api.hist_p_change(hist_data, begin=30, end=50)
d = api.normalizing_std_close(hist_data, begin=30, end=50)
print(c)
print(d)
# print(histData)
# print(api.normalizing_std_close(histData, 1, 11))
# print([1, 2, 3, 5][:2])
# print(1.1 ** 28)

# h = [1, 1.2, 1.2**2, 1.2**3, 1.2**4]
# print(h)
# print(np.mean(h))
# print(np.std(h) / np.mean(h))
#
# print((1.2**5 - np.mean(h)) / np.std(h))

# basics = ts.get_stock_basics()
#
#
# print(basics)