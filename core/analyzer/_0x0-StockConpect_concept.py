# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.core.analyzer.api as api

import midas.core.data.models as models
from midas.core.data.engine import main_session

COL_CONCEPT_COUNT = 'COL_CONCEPT_COUNT'


def main():
    data_frame = DataFrame()
    for i, concept in enumerate(main_session.query(models.ConceptPro).all()):
        try:
            data_frame.loc[i, 'concept_name'] = concept.name
            stock_value = ''
            for detail in main_session.query(models.ConceptDetailPro).filter(models.ConceptDetailPro.code == concept.code).all():
                stock_value = stock_value + '{ts_code} {name}\n'.format(ts_code=detail.ts_code, name=detail.name)
            data_frame.loc[i, 'stock'] = stock_value
        except Exception as e:
            print('excetion in index:{index} {code} {name}'.format(index=i, code=concept.code, name=concept.name))
            continue
        print('##### {i} #####'.format(i=i))

    file_name = '../../cookbook/@StockConcept_concept.csv'
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)


if __name__ == '__main__':
    main()