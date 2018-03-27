# -*- coding: utf-8 -*-
import tushare as ts
import midas.midas.api as api

histData = ts.get_hist_data('000655')
print(api.normalizing_std_close(histData, 1, 11))
# print([1, 2, 3, 5][:2])
# print(1.1 ** 28)