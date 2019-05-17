# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.analyzer.api as api

import midas.midas.data.models as models
from midas.midas.data.engine import main_session

COL_MA_5 = 'COL_MA_5'
COL_MA_10 = 'COL_MA_10'
COL_MA_20 = 'COL_MA_20'
COL_MA_5_SLOPE = 'COL_MA_5_SLOPE'
COL_MA_10_SLOPE = 'COL_MA_10_SLOPE'
COL_MA_20_SLOPE = 'COL_MA_20_SLOPE'
COL_LASTPRICE = 'COL_LASTPRICE'
COL_MA_CLOSE_GAP = 'COL_MA_CLOSE_GAP'

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
            ma_5 = api.daily_close_ma(daily=daily, step=5)
            ma_10 = api.daily_close_ma(daily=daily, step=10)
            ma_20 = api.daily_close_ma(daily=daily, step=20)
            data_frame.loc[i, COL_MA_5] = ma_5[0]
            data_frame.loc[i, COL_MA_10] = ma_10[0]
            data_frame.loc[i, COL_MA_20] = ma_20[0]
            data_frame.loc[i, COL_MA_5_SLOPE] = round((ma_5[0] / ma_5[1] - 1) * 100, 2)
            data_frame.loc[i, COL_MA_10_SLOPE] = round((ma_10[0] / ma_10[1] - 1) * 100, 2)
            data_frame.loc[i, COL_MA_20_SLOPE] = round((ma_20[0] / ma_20[1] - 1) * 100, 2)
            data_frame.loc[i, COL_LASTPRICE] = daily[0].close
            data_frame.loc[i, COL_MA_CLOSE_GAP] = round((data_frame.loc[i, COL_LASTPRICE] / data_frame.loc[i, COL_MA_20] - 1) * 100, 2)
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
                            (data_frame[COL_MA_5] > data_frame[COL_MA_10])
                            & (data_frame[COL_MA_10] > data_frame[COL_MA_20])
                            # & (data_frame[COL_MA_5_SLOPE] > data_frame[COL_MA_10_SLOPE])
                            # & (data_frame[COL_MA_10_SLOPE] > data_frame[COL_MA_20_SLOPE])
                            & (data_frame[COL_MA_CLOSE_GAP] > 0)
                           ]
    # data_frame = data_frame.sort_values(by=COL_MAXGAP, ascending=False).reset_index(drop=True)
    # data_frame = data_frame.iloc[:200]

    data_frame = data_frame.sort_values(by=COL_MA_CLOSE_GAP, ascending=True).reset_index(drop=True)

    file_name = '../../logs/{date}@MA_walker.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)


if __name__ == '__main__':
    main(offset=0)