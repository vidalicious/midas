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

sampling_count = 100


@update_to_db(main_session)
def main():
    pro = ts.pro_api()
    trade_dates = pro.daily(ts_code='000001.SZ').trade_date
    LAST_MARKET_DATE = trade_dates[0]

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

    main_session.query(models.DailyPro).delete()
    main_session.commit()
    for count, sbp in enumerate(main_session.query(models.StockBasicPro).all()):
        try:
            daily = pro.daily(ts_code=sbp.ts_code, start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
        except Exception as e:
            print('excetion in {}'.format(count))
            continue

        for i in range(len(daily)):
            a_daily = models.DailyPro(ts_code=daily.loc[i, 'ts_code'],
                                      trade_date=daily.loc[i, 'trade_date'],
                                      open=float(daily.loc[i, 'open']),
                                      high=float(daily.loc[i, 'high']),
                                      low=float(daily.loc[i, 'low']),
                                      close=float(daily.loc[i, 'close']),
                                      pre_close=float(daily.loc[i, 'pre_close']),
                                      change=float(daily.loc[i, 'change']),
                                      pct_chg=float(daily.loc[i, 'pct_chg']),
                                      vol=float(daily.loc[i, 'vol']),
                                      amount=float(daily.loc[i, 'amount'])
                                      )
            main_session.add(a_daily)
        main_session.commit()
        print('##### {i} #####'.format(i=count))
        time.sleep(0.1)


if __name__ == '__main__':
    main()