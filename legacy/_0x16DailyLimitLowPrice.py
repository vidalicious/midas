# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.core.analyzer.api as api

import midas.core.data.models as models
from midas.core.data.engine import main_session

COL_CONTINUOUS_LIMIT = 'COL_CONTINUOUS_LIMIT'
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

            data_frame.loc[i, COL_CONTINUOUS_LIMIT] = api.daily_continuous_limit_count(daily=daily)
            data_frame.loc[i, COL_LASTPRICE] = daily[0].close

            cons = main_session.query(models.ConceptPro).join(models.ConceptDetailPro,
                                                              models.ConceptPro.code == models.ConceptDetailPro.code).filter(
                models.ConceptDetailPro.ts_code == stock_basic.ts_code).all()
            concept_value = ''
            for con in cons:
                concept_value = concept_value + '{c}, '.format(c=con.name)
            data_frame.loc[i, 'concept'] = concept_value

            daily_basic = main_session.query(models.DailyBasicPro).filter(models.DailyBasicPro.ts_code == stock_basic.ts_code).first()
            if daily_basic:
                data_frame.loc[i, 'circ_mv'] = '{}亿'.format(round(daily_basic.circ_mv / 10000, 2))

        except Exception as e:
            print('excetion in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### {i} #####'.format(i=i))

    data_frame = data_frame[
                            (data_frame[COL_CONTINUOUS_LIMIT] > 0)
                           ]

    sorted_frame = data_frame.sort_values(by=COL_LASTPRICE, ascending=True).reset_index(drop=True)

    file_name = '../../logs/{date}@DailyLimitLowPrice.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)
    return sorted_frame


if __name__ == '__main__':
    main(0)