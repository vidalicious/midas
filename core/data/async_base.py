# -*- coding: utf-8 -*-
import time

import tushare as ts

import midas.core.data.models as models
from midas.core.data.engine import main_session
from midas.core.data.engine import update_to_db

sampling_count = 40

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


def async_daily():
    main_session.query(models.DailyPro).delete()
    main_session.commit()
    for count, sbp in enumerate(main_session.query(models.StockBasicPro).all()):
        if_pass = False
        while not if_pass:
            try:
                daily = pro.daily(ts_code=sbp.ts_code, start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
                if_pass = True
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
        time.sleep(0.15)


def async_daily_basic():
    main_session.query(models.DailyBasicPro).delete()
    main_session.commit()
    for count, sbp in enumerate(main_session.query(models.StockBasicPro).all()):
        try:
            daily_basic = pro.daily_basic(ts_code=sbp.ts_code, trade_date=LAST_MARKET_DATE)
            a_daily_basic = models.DailyBasicPro(ts_code=daily_basic.loc[0, 'ts_code'],
                                                 trade_date=daily_basic.loc[0, 'trade_date'],
                                                 turnover_rate=float(daily_basic.loc[0, 'turnover_rate']),
                                                 turnover_rate_f=float(daily_basic.loc[0, 'turnover_rate_f']),
                                                 total_share=float(daily_basic.loc[0, 'total_share']),
                                                 float_share=float(daily_basic.loc[0, 'float_share']),
                                                 free_share=float(daily_basic.loc[0, 'free_share']),
                                                 total_mv=float(daily_basic.loc[0, 'total_mv']),
                                                 circ_mv=float(daily_basic.loc[0, 'circ_mv']))
        except Exception as e:
            print('excetion in {}'.format(count))
            continue

        main_session.add(a_daily_basic)
        main_session.commit()
        print('##### {i} #####'.format(i=count))
        time.sleep(0.15)


@update_to_db(main_session)
def main():
    async_stock_basic()
    async_daily()
    # async_daily_basic()


if __name__ == '__main__':
    main()