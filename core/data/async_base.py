# -*- coding: utf-8 -*-
import time
import requests
import tushare as ts

import midas.core.data.models as models
from midas.core.data.engine import main_session
from midas.core.data.engine import update_to_db
from pandas import DataFrame

sampling_count = 150

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
def async_daily():
    main_session.query(models.DailyPro).delete()
    main_session.commit()
    for count, sbp in enumerate(main_session.query(models.StockBasicPro).all()):
        if_pass = False
        while not if_pass:
            try:
                daily = ts.pro_bar(ts_code=sbp.ts_code, adj='qfq', start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
                if_pass = True
            except Exception as e:
                print('exception in {}'.format(count))
                continue

        if not isinstance(daily, DataFrame):
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
        print('##### async_daily {i} #####'.format(i=count))
        time.sleep(0.2)


@update_to_db(main_session)
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
        print('##### async_daily_basic {i} #####'.format(i=count))
        time.sleep(0.2)

# /**
#  * 股票接口
#  *
#  *  http://sqt.gtimg.cn/utf8/q=股票代码01,股票代码02&offset=1,2,3,4,31,32,33,38
#  *                                                offset返回结果字段的索引号
#  *   返回结果样例：v_sh600887="1
#  *            2            ~伊利股份                     股票名称
#  *            3            ~600887                      股票代码
#  *            4            ~16.32                       最新报价
#  *            5            ~16.31                       昨收
#  *            6            ~16.31                       今开
#  *            7            ~180204                      成交量(手)。除以100后单位为：万股
#  *            8            ~94954                       外盘
#  *            9            ~85250                       内盘
#  *           10            ~16.31                       五档盘口:买01:元
#  *           11            ~33                          五档盘口:买01:手
#  *           12            ~16.30                       五档盘口:买02:元
#  *           13            ~912                         五档盘口:买02:手
#  *           14            ~16.29                       五档盘口:买03:元
#  *           15            ~264                         五档盘口:买03:手
#  *           16            ~16.28                       五档盘口:买04:元
#  *           17            ~591                         五档盘口:买04:手
#  *           18            ~16.27                       五档盘口:买05:元
#  *           19            ~194                         五档盘口:买05:手
#  *           20            ~16.32                       五档盘口:卖01:元
#  *           21            ~793                         五档盘口:卖01:手
#  *           22            ~16.33                       五档盘口:卖02:元
#  *           23            ~1976                        五档盘口:卖02:手
#  *           24            ~16.34                       五档盘口:卖03:元
#  *           25            ~662                         五档盘口:卖03:手
#  *           26            ~16.35                       五档盘口:卖04:元
#  *           27            ~1217                        五档盘口:卖04:手
#  *           28            ~16.36                       五档盘口:卖05:元
#  *           29            ~461                         五档盘口:卖05:手
#  *           30            ~15:00:02/16.32/63/B/102774/13108|14:59:56/16.32/60/B/97890/13103|14:59:47/16.32/98/B/159893/13095|14:59:47/16.32/148/B/241481/13092|14:59:41/16.32/162/B/264330/13087|14:59:37/16.32/139/B/226781/13084
#  *           31            ~20160622150541              时间
#  *           32            ~0.01                        涨跌额（单位：元）
#  *           33            ~0.06                        涨跌幅 %
#  *           34            ~16.42                       今日最高
#  *           35            ~16.16                       今日最低
#  *           36            ~16.32/180141/293078740
#  *           37            ~180204                      成交量(手)。除以100后单位为：万股
#  *           38            ~29318                       成交额（单位：万元）
#  *           39            ~0.30                        换手率 %
#  *           40            ~20.27                       市盈率
#  *           41            ~
#  *           42            ~16.42
#  *           43            ~16.16
#  *           44            ~1.59                        振幅 %
#  *           45            ~984.65                      流通市值（单位：亿元）
#  *           46            ~989.78                      总市值（单位：亿元）
#  *           47            ~4.59                        市净率
#  *           48            ~17.94
#  *           49            ~14.68
#  *           50            ~";


@update_to_db(main_session)
def async_daily_basic_origin():
    main_session.query(models.DailyBasic).delete()
    main_session.commit()
    for count, sbp in enumerate(main_session.query(models.StockBasicPro).all()):
        market = sbp.ts_code.split('.')[1].lower()
        symbol = sbp.symbol
        code = market + symbol

        if_pass = False
        while not if_pass:
            try:
                res = requests.get('http://sqt.gtimg.cn/q={}'.format(code))
                if_pass = True
            except Exception as e:
                print('exception in {}'.format(count))
                continue

        try:
            res = res.text.split('~')
            a_daily_basic = models.DailyBasic(
                ts_code=sbp.ts_code,
                name=sbp.name,
                trade_date=LAST_MARKET_DATE,
                total_mv=float(res[45]) if res[45] else 0,
                circ_mv=float(res[44]) if res[44] else 0
            )
        except Exception as e:
            continue

        main_session.add(a_daily_basic)
        main_session.commit()
        print('##### async_daily_basic_origin {i} #####'.format(i=count))


def main():
    # async_stock_basic()
    async_daily_basic_origin()
    # async_daily_basic()


if __name__ == '__main__':
    main()