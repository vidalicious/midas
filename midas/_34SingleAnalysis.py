# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.api_pro as api

ts_code = '000993.SZ'

sampling_count = 100

pro = ts.pro_api()

trade_dates = pro.daily(ts_code='000001.SZ').trade_date
LAST_MARKET_DATE = trade_dates[4]

daily = pro.daily(ts_code=ts_code, start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
a = api.daily_weight_eigen_slope(daily=daily, begin=0, end=5)
b = api.daily_weight_eigen_slope(daily=daily, begin=5, end=10)
c = api.daily_limit_up_count(daily=daily, begin=0, end=10)

pass

# print('analysis {code}'.format(code=ts_code))
# for i in range(0, 5):
#     (weight_rise_efficiency, weight_min_index, weight_max_index) = api.daily_weight_rise_efficiency(daily=daily, begin=5 * i, end=20 + 5 * i)
#     print('weight_rise_efficiency, weight_min_index, weight_max_index: {efficiency}, {min}, {max}'.format(
#         efficiency=weight_rise_efficiency, min=weight_min_index, max=weight_max_index))

