# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.api_pro as api
import midas.midas.data.models as models
from midas.midas.data.engine import main_session
from midas.midas.data.engine import update_to_db

sampling_count = 200

pro = ts.pro_api()
trade_dates = pro.daily(ts_code='000001.SZ').trade_date
LAST_MARKET_DATE = trade_dates[0]


def async_stock_basic():
    main_session.query(models.StockBasicPro).delete()
    main_session.commit()
    stock_basic = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,industry,fullname')
    for i in range(len(stock_basic)):
        a_stock_basic = models.StockBasicPro(ts_code=stock_basic.loc[i, 'ts_code'],
                                             symbol=stock_basic.loc[i, 'symbol'],
                                             name=stock_basic.loc[i, 'name'],
                                             industry=stock_basic.loc[i, 'industry']
                                             )
        main_session.add(a_stock_basic)

    main_session.commit()
    print('##### async stock basic finished #####')


def async_weekly():
    main_session.query(models.WeeklyPro).delete()
    main_session.commit()
    for count, sbp in enumerate(main_session.query(models.StockBasicPro).all()):
        try:
            weekly = pro.weekly(ts_code=sbp.ts_code, start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
        except Exception as e:
            print('excetion in {}'.format(count))
            continue

        for i in range(len(weekly)):
            a_weekly = models.WeeklyPro(ts_code=weekly.loc[i, 'ts_code'],
                                      trade_date=weekly.loc[i, 'trade_date'],
                                      open=float(weekly.loc[i, 'open']),
                                      high=float(weekly.loc[i, 'high']),
                                      low=float(weekly.loc[i, 'low']),
                                      close=float(weekly.loc[i, 'close']),
                                      pre_close=float(weekly.loc[i, 'pre_close']),
                                      change=float(weekly.loc[i, 'change']),
                                      pct_chg=float(weekly.loc[i, 'pct_chg']),
                                      vol=float(weekly.loc[i, 'vol']),
                                      amount=float(weekly.loc[i, 'amount'])
                                      )
            main_session.add(a_weekly)
        main_session.commit()
        print('##### {i} #####'.format(i=count))
        time.sleep(0.3)


@update_to_db(main_session)
def main():
    async_stock_basic()
    async_weekly()


if __name__ == '__main__':
    main()