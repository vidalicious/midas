# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.analyzer.api as api

import midas.midas.data.models as models
from midas.midas.data.engine import main_session

COL_WEIGHT_RISE_EFFICIENCY = 'COL_WEIGHT_RISE_EFFICIENCY'
COL_WEIGHT_MIN_INDEX = 'COL_WEIGHT_MIN_INDEX'
COL_WEIGHT_MAX_INDEX = 'COL_WEIGHT_MAX_INDEX'
COL_LASTPRICE = 'COL_LASTPRICE'

sampling_count = 40


def main(offset=0):
    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    LAST_MARKET_DATE = daily001[offset].trade_date

    data_frame = DataFrame()
    for i, stock_basic in enumerate(main_session.query(models.StockBasicPro).all()):
        try:
            for key in models.StockBasicPro.keys:
                data_frame.loc[i, key] = getattr(stock_basic, key)

            daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == stock_basic.ts_code,
                                                               models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(
                models.DailyPro.trade_date.desc()).limit(sampling_count).all()
            (data_frame.loc[i, COL_WEIGHT_RISE_EFFICIENCY],
             data_frame.loc[i, COL_WEIGHT_MIN_INDEX],
             data_frame.loc[i, COL_WEIGHT_MAX_INDEX]) = api.daily_weight_rise_efficiency(daily=daily, begin=0, end=10)

            data_frame.loc[i, COL_LASTPRICE] = daily[0].close
        except Exception as e:
            print('excetion in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### {i} #####'.format(i=i))

    data_frame = data_frame[
                            (data_frame[COL_WEIGHT_RISE_EFFICIENCY] > 2)
                            & (data_frame[COL_WEIGHT_MAX_INDEX] < 2)
                           ]

    sorted_frame = data_frame.sort_values(by=COL_WEIGHT_RISE_EFFICIENCY, ascending=False).reset_index(drop=True)

    file_name = '../../logs/{date}@RiseTempo.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)
    return sorted_frame


if __name__ == '__main__':
    main()