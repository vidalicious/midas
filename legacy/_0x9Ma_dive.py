# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.core.analyzer.api as api

import midas.core.data.models as models
from midas.core.data.engine import main_session

COL_MA_A = 'COL_MA_A'
COL_MA_B = 'COL_MA_B'
COL_MA_GAP = 'COL_MA_GAP'
COL_LASTPRICE = 'COL_LASTPRICE'

sampling_count = 40


def main(ma_a=10, ma_b=20):
    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    LAST_MARKET_DATE = daily001[0].trade_date

    data_frame = DataFrame()
    for i, stock_basic in enumerate(main_session.query(models.StockBasicPro).all()):
        try:
            for key in models.StockBasicPro.keys:
                data_frame.loc[i, key] = getattr(stock_basic, key)

            daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == stock_basic.ts_code,
                                                               models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(
                models.DailyPro.trade_date.desc()).limit(sampling_count).all()
            data_frame.loc[i, COL_MA_A] = api.daily_close_ma(daily=daily, step=ma_a)[0]
            data_frame.loc[i, COL_MA_B] = api.daily_close_ma(daily=daily, step=ma_b)[0]
            data_frame.loc[i, COL_MA_GAP] = round((data_frame.loc[i, COL_MA_A] / data_frame.loc[i, COL_MA_B] - 1) * 100, 2)
            data_frame.loc[i, COL_LASTPRICE] = daily[0].close

            cons = main_session.query(models.ConceptPro).join(models.ConceptDetailPro,
                                                              models.ConceptPro.code == models.ConceptDetailPro.code).filter(
                models.ConceptDetailPro.ts_code == stock_basic.ts_code).all()
            concept_value = ''
            for con in cons:
                concept_value = concept_value + '{c}, '.format(c=con.name)
            data_frame.loc[i, 'concept'] = concept_value
        except Exception as e:
            print('excetion in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### {i} #####'.format(i=i))

    data_frame = data_frame[
                            (data_frame[COL_MA_GAP] > 0)
                           ]
    # data_frame = data_frame.sort_values(by=COL_MAXGAP, ascending=False).reset_index(drop=True)
    # data_frame = data_frame.iloc[:200]

    data_frame = data_frame.sort_values(by=COL_MA_GAP, ascending=True).reset_index(drop=True)

    file_name = '../../logs/{date}@Ma_dive_ma{ma_a}_ma{ma_b}.csv'.format(date=LAST_MARKET_DATE, ma_a=ma_a, ma_b=ma_b)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)


if __name__ == '__main__':
    main()