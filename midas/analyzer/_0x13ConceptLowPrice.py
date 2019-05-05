# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.analyzer.api as api

import midas.midas.data.models as models
from midas.midas.data.engine import main_session


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

            data_frame.loc[i, COL_LASTPRICE] = daily[0].close

            cons = main_session.query(models.ConceptPro).join(models.ConceptDetailPro,
                                                                  models.ConceptPro.code == models.ConceptDetailPro.code).filter(
                models.ConceptDetailPro.ts_code == ts_code).all()
            concept_value = ''
            for con in cons:
                concept_value = concept_value + '{c}, '.format(c=con.name)
            data_frame.loc[i, 'concept'] = concept_value
        except Exception as e:
            print('excetion in index:{index} {code}'.format(index=i, code=ts_code))
            continue
        print('##### {i} #####'.format(i=i))

    sorted_frame = data_frame.sort_values(by=COL_LASTPRICE, ascending=True).reset_index(drop=True)

    title = ''
    for concept in concepts:
        if len(title) == 0:
            title = title + concept
        else:
            title = title + '+{}'.format(concept)
    file_name = '../../logs/{date}@{concept}@ConceptLowPrice.csv'.format(date=LAST_MARKET_DATE, concept=title)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)
    return sorted_frame


if __name__ == '__main__':
    # main(concepts=['无人驾驶'])
    # main(concepts=['5G'])
    # main(concepts=['军工'])
    # main(concepts=['养猪'])
    # main(concepts=['燃料电池'])
    # main(concepts=['工业大麻'])
    # main(concepts=['一带一路'])
    # main(concepts=['区块链'])
    # main(concepts=['强势人气股'])
    # main(concepts=['染料'])
    main(concepts=['业绩预增'])
    # main(concepts=['5G','央企改革'])
    # main(concepts=['光', '5G','石墨烯'])

