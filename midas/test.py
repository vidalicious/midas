# -*- coding: utf-8 -*-
import tushare as ts
import midas.midas.api_pro as api
import numpy as np
import re
import time
import datetime

hist_data = ts.get_hist_data('000622')
# a = api.hist_p_change(hist_data, begin=18, end=30)
# b = api.hist_daily_hairy(hist_data, begin=0, end=5)
# print(a)
# print(b)
#
# c = api.hist_p_change(hist_data, begin=30, end=50)
# d = api.normalizing_std_close(hist_data, begin=30, end=50)
# print(c)
# print(d)
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

pro = ts.pro_api()
# daily_basic = pro.daily_basic(ts_code='600604.SH',
#                               start_date='20181023', end_date='20181207')
daily = pro.daily(ts_code='002803.SZ')

a = api.daily_max_jump_p_change(daily, end=30)
pro = ts.pro_api()
daily_basic = pro.daily_basic(ts_code='600604.SH',
                              start_date='20181023', end_date='20181207')
daily = pro.daily(ts_code='603066.SH')

a = api.daily_break_continuously_high_fall_count(daily)
pass

# pattern = '[a-zA-Z]+'
# search = re.search(pattern, 'fir_AS')
# if search:
#     version = search.group()
#     pass
#
# a = 'AAA-BBB_ccc'.lower()
# pass
#
# a = type(dict()).__name__
b = time.time()
c = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
trade_dates = pro.daily(ts_code='000001.SZ').trade_date
pass
