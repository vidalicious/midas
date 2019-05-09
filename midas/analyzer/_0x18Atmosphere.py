# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.analyzer.api as api

import midas.midas.data.models as models
from midas.midas.data.engine import main_session


sampling_count = 40


def main(offset=0):
    limit_up = 0
    limit_down = 0
    positive = 0
    negative = 0
    more_than_5 = 0
    less_than_minus_5 = 0
    total = 0

    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    LAST_MARKET_DATE = daily001[offset].trade_date

    data_frame = DataFrame()
    for i, stock_basic in enumerate(main_session.query(models.StockBasicPro).all()):
        try:
            daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == stock_basic.ts_code,
                                                               models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(
                models.DailyPro.trade_date.desc()).limit(sampling_count).first()
            if daily:
                if daily.pct_chg > 9.9:
                    limit_up = limit_up + 1
                if daily.pct_chg < -9.9:
                    limit_down = limit_down + 1
                if daily.pct_chg >= 0:
                    positive = positive + 1
                if daily.pct_chg < 0:
                    negative = negative + 1
                if daily.pct_chg > 5:
                    more_than_5 = more_than_5 + 1
                if daily.pct_chg < -5:
                    less_than_minus_5 = less_than_minus_5 + 1

                total = total + 1

        except Exception as e:
            print('excetion in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### {i} #####'.format(i=i))

    data_frame.loc[0, '涨停'] = limit_up
    data_frame.loc[0, '跌停'] = limit_down
    data_frame.loc[0, '涨'] = round(positive / total, 2)
    data_frame.loc[0, '跌'] = round(negative / total, 2)
    data_frame.loc[0, '> 5%'] = round(more_than_5 / total, 2)
    data_frame.loc[0, '< -5%'] = round(less_than_minus_5 / total, 2)

    file_name = '../../logs/{date}@Atmosphere.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)


if __name__ == '__main__':
    main(offset=0)