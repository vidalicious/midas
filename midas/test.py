# -*- coding: utf-8 -*-
import tushare as ts

histData = ts.get_hist_data('002069')
print(histData)