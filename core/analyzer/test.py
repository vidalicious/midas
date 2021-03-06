# -*- coding: utf-8 -*-

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


import numpy as np
import pandas as pd
import seaborn as sns
sns.set_theme(style="whitegrid")

rs = np.random.RandomState(365)
values = rs.randn(365, 4).cumsum(axis=0)
dates = pd.date_range("1 1 2016", periods=365, freq="D")
data = pd.DataFrame(values, dates, columns=["A", "B", "C", "D"])
data = data.rolling(7).mean()

sns.lineplot(data=data, palette="tab10", linewidth=2.5)

import seaborn as sns

flights = sns.load_dataset("flights")
flights_wide = flights.pivot("year", "month", "passengers")
flights_wide.head()
sns.lineplot(data=flights_wide)


a = [1, 2, 3, 4, 5, 6, 7]
b = a[:50]

import requests
a = requests.get('http://sqt.gtimg.cn/q=sh605168')
b = a.text.split('~')


import tushare as ts
pro = ts.pro_api()
trade_dates = pro.daily(ts_code='000001.SZ').trade_date

import midas.core.analyzer.api as api

import midas.core.data.models as models
from midas.core.data.engine import main_session
import midas.bin.env as env
# daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '002979.SZ'
#                                                    ).all()
#
# daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(
#     models.DailyPro.trade_date.desc()).all()
#
# dates = [daily001[i].trade_date for i in range(150)]
# a = dates.index(20200512)
# b = dates.index(20200123)
# print()

basic = main_session.query(models.StockBasicPro).all()
for item in basic:

    print('{code} {name} {industry}'.format(code=item.ts_code, name=item.name, industry=item.industry))