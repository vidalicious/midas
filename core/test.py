# -*- coding: utf-8 -*-
import requests

import tushare as ts
#
# headers = {
#     'Content-Type': 'application/json; charset=UTF-8',
#     'Authorization': 'APPCODE ' + 'a541d723a1874f329f0e63dd3c6cdac4'
# }
#
# json = {
#     "prod_code_obj_grp": [
#         {
#             "prod_code": "300362",
#             "hq_type_code": "XSHE"
#         },
#         {
#             "prod_code": "300218",
#             "hq_type_code": "XSHE"
#         },
#     ]
# }
# url = 'http://costdis.market.alicloudapi.com/quote/v2/qplus/cost_distribution/get_stock_chip'
# a = requests.post(url=url, headers=headers, json=json)
# print(a.json())


pro = ts.pro_api()
df1 = pro.top_inst(trade_date='20200414', ts_code='000001.SZ')
df2 = pro.top_list(trade_date='20200414')
a = df1.to_dict()
b = df2.to_dict()
# trade_dates = pro.daily(ts_code='000001.SZ').trade_date
# LAST_MARKET_DATE = trade_dates[0]
# BEGIN_MARKET_DATE = trade_dates[100]
#
# df = pro.top10_floatholders(ts_code='600052.SH', start_date=BEGIN_MARKET_DATE, end_date=LAST_MARKET_DATE)
#
# daily = pro.daily(ts_code='600052.SH', start_date=trade_dates[100], end_date=LAST_MARKET_DATE)

pass