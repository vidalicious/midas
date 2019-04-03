# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.analyzer.api as api

import midas.midas.data.models as models
from midas.midas.data.engine import main_session

COL_CONCEPT_COUNT = 'COL_CONCEPT_COUNT'


def main():
    data_frame = DataFrame()
    for i, stock_basic in enumerate(main_session.query(models.StockBasicPro).all()):
        try:
            for key in ['ts_code', 'name']:
                data_frame.loc[i, key] = getattr(stock_basic, key)

            concepts = main_session.query(models.ConceptPro).join(models.ConceptDetailPro,
                models.ConceptPro.code == models.ConceptDetailPro.code).filter(models.ConceptDetailPro.ts_code == stock_basic.ts_code).all()
            concept_value = ''
            for concept in concepts:
                concept_value = concept_value + '{c}, '.format(c=concept.name)

            data_frame.loc[i, 'concept'] = concept_value
            data_frame.loc[i, COL_CONCEPT_COUNT] = len(concepts)
        except Exception as e:
            print('excetion in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### {i} #####'.format(i=i))

    sorted_frame = data_frame.sort_values(by=COL_CONCEPT_COUNT, ascending=False).reset_index(drop=True)

    file_name = '../../cookbook/@StockConcept_stock.csv'
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)


if __name__ == '__main__':
    main()