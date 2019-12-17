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
trade_dates = pro.daily(ts_code='000001.SZ').trade_date
LAST_MARKET_DATE = trade_dates[0]
BEGIN_MARKET_DATE = trade_dates[100]

df = pro.top10_floatholders(ts_code='600615.SH', start_date=BEGIN_MARKET_DATE, end_date=LAST_MARKET_DATE)

pass