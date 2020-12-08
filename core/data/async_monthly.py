# -*- coding: utf-8 -*-
import time

import tushare as ts

import midas.core.data.models as models
from midas.core.data.engine import main_session
from midas.core.data.engine import update_to_db

sampling_count = 1000

pro = ts.pro_api()
trade_dates = pro.daily(ts_code='000001.SZ').trade_date
LAST_MARKET_DATE = trade_dates[0]


@update_to_db(main_session)
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


@update_to_db(main_session)
def async_monthly():
    main_session.query(models.MonthlyPro).delete()
    main_session.commit()
    for count, sbp in enumerate(main_session.query(models.StockBasicPro).all()):
        if_pass = False
        while not if_pass:
            try:
                monthly = pro.monthly(ts_code=sbp.ts_code, start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
                if_pass = True
            except Exception as e:
                print('exception in {}'.format(count))
                continue

        for i in range(len(monthly)):
            a_monthly = models.MonthlyPro(ts_code=monthly.loc[i, 'ts_code'],
                                      trade_date=monthly.loc[i, 'trade_date'],
                                      open=float(monthly.loc[i, 'open']),
                                      high=float(monthly.loc[i, 'high']),
                                      low=float(monthly.loc[i, 'low']),
                                      close=float(monthly.loc[i, 'close']),
                                      pre_close=float(monthly.loc[i, 'pre_close']),
                                      change=float(monthly.loc[i, 'change']),
                                      pct_chg=float(monthly.loc[i, 'pct_chg']),
                                      vol=float(monthly.loc[i, 'vol']),
                                      amount=float(monthly.loc[i, 'amount'])
                                      )
            main_session.add(a_monthly)
        main_session.commit()
        print('##### async_monthly {i} #####'.format(i=count))
        time.sleep(0.2)


def main():
    async_stock_basic()
    async_monthly()


if __name__ == '__main__':
    main()