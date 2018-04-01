# -*- coding: utf-8 -*-
import tushare as ts
import midas.midas.api as api
import numpy as np

histData = ts.get_hist_data('000655')
print(histData)
# print(api.normalizing_std_close(histData, 1, 11))
# print([1, 2, 3, 5][:2])
# print(1.1 ** 28)

h = [1, 1.2, 1.2**2, 1.2**3, 1.2**4]
print(h)
print(np.mean(h))
print(np.std(h) / np.mean(h))

print((1.2**5 - np.mean(h)) / np.std(h))