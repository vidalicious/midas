# -*- coding: utf-8 -*-
import tushare as ts

histData = ts.get_hist_data('601600')
print(histData)
# print([1, 2, 3, 5][:2])
# print(1.1 ** 28)