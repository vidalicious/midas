# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.analyzer.api as api

import midas.midas.data.models as models
from midas.midas.data.engine import main_session
import midas.midas.analyzer._0x3MinusCombo as combo

# df0 = combo.main(0)
# df1 = combo.main(1)
#
# l = list()
# for i, item0 in df0.iterrows():
#     for j, item1 in df1.iterrows():
#         if item0.ts_code == item1.ts_code:
#             l.append('{code} {name}'.format(code=item0.ts_code, name=item0.name))
#
# print(l)

# daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(
#     models.DailyPro.trade_date.desc()).all()
# LAST_MARKET_DATE = daily001[0].trade_date
# daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '600197.SH',
#                                                    models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(
#     models.DailyPro.trade_date.desc()).limit(40).all()
#
# a = api.daily_limit_period(daily=daily, begin=0, end=15)
# pass
# pro = ts.pro_api()
# df = pro.concept()
# a = pro.concept_detail(id='TS2', fields='ts_code,name')
# pass

for i in range(1):
    print(i)

a = [0, 1, 2,3,4]
print(a[0:4])