# -*- coding: utf-8 -*-
import tushare as ts

histData = ts.get_hist_data('603637')
print(histData)

# print(1.1 ** 28)