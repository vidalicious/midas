# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.analyzer.api as api

import midas.midas.data.models as models
from midas.midas.data.engine import main_session


COL_EIGEN_SLOPE = 'COL_EIGEN_SLOPE'
COL_LAST_PCT_CHG = 'COL_LAST_PCT_CHG'
COL_LASTPRICE = 'COL_LASTPRICE'

sampling_count = 40


def main(concepts=[], offset=0):
    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    LAST_MARKET_DATE = daily001[offset].trade_date

    data_frame = DataFrame()
    ts_codes = set()
    for concept in concepts:
        details = main_session.query(models.ConceptDetailPro).join(models.ConceptPro,
            models.ConceptDetailPro.code == models.ConceptPro.code).filter(models.ConceptPro.name.like('%{concept}%'.format(concept=concept))).all()
        if details:
            ts_codes_buff = set()
            for detail in details:
                ts_codes_buff.add(detail.ts_code)
            if len(ts_codes) > 0:
                ts_codes = ts_codes & ts_codes_buff
            else:
                ts_codes = ts_codes_buff

    for i, ts_code in enumerate(ts_codes):
        try:
            basic = main_session.query(models.StockBasicPro).filter(models.StockBasicPro.ts_code == ts_code).first()
            for key in models.StockBasicPro.keys:
                data_frame.loc[i, key] = getattr(basic, key)

            daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == ts_code,
                                                               models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(
                models.DailyPro.trade_date.desc()).limit(sampling_count).all()

            data_frame.loc[i, COL_EIGEN_SLOPE] = api.daily_weight_eigen_slope(daily=daily, begin=0, end=5)
            data_frame.loc[i, COL_LAST_PCT_CHG] = daily[0].pct_chg
            data_frame.loc[i, COL_LASTPRICE] = daily[0].close

        except Exception as e:
            print('excetion in index:{index} {code}'.format(index=i, code=ts_code))
            continue
        print('##### {i} #####'.format(i=i))

    sorted_frame = data_frame.sort_values(by=COL_LAST_PCT_CHG, ascending=False).reset_index(drop=True)

    title = ''
    for concept in concepts:
        if len(title) == 0:
            title = title + concept
        else:
            title = title + '+{}'.format(concept)
    file_name = '../../logs/{date}@{concept}@ConceptLadder.csv'.format(date=LAST_MARKET_DATE, concept=title)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)
    return sorted_frame


if __name__ == '__main__':
    main(concepts=['5G'])