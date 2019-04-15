# -*- coding: utf-8 -*-
import json
import time
import heapq

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.analyzer.api as api

import midas.midas.data.models as models
from midas.midas.data.engine import main_session

COL_CONCEPT = 'COL_CONCEPT'
COL_AVERAGE_EIGEN_SLOPE = 'COL_AVERAGE_EIGEN_SLOPE'

sampling_count = 40
GAP = 10


def main(offset=0):
    cache = dict()

    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    LAST_MARKET_DATE = daily001[offset].trade_date

    data_frame = DataFrame()
    for i, concept in enumerate(main_session.query(models.ConceptPro).all()):
        eigens = list()
        for concept_detail in main_session.query(models.ConceptDetailPro).filter(
                models.ConceptDetailPro.code == concept.code).all():
            try:
                if concept_detail.ts_code in cache:
                    es = cache[concept_detail.ts_code]
                else:
                    daily = main_session.query(models.DailyPro).filter(
                        models.DailyPro.ts_code == concept_detail.ts_code,
                        models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(
                        models.DailyPro.trade_date.desc()).limit(sampling_count).all()
                    es = api.daily_weight_eigen_slope(daily=daily, begin=0, end=GAP)
                    cache[concept_detail.ts_code] = es

                eigens.append(es)
            except Exception as e:
                print('excetion in {code} {name}'.format(code=concept_detail.ts_code, name=concept_detail.name))
                continue

        data_frame.loc[i, COL_CONCEPT] = concept.name
        top_5 = heapq.nlargest(5, eigens)
        data_frame.loc[i, COL_AVERAGE_EIGEN_SLOPE] = round(np.mean(top_5), 2)
        print('##### {i} #####'.format(i=i))

    sorted_frame = data_frame.sort_values(by=COL_AVERAGE_EIGEN_SLOPE, ascending=False).reset_index(drop=True)

    file_name = '../../logs/{date}@ConceptAverageEigenSlope.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)
    return sorted_frame


if __name__ == '__main__':
    main()