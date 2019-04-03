# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.analyzer.api as api

import midas.midas.data.models as models
from midas.midas.data.engine import main_session


def main():
    data_frame = DataFrame()
    for i, stock_basic in enumerate(main_session.query(models.StockBasicPro).all()):
        try:
            for key in ['ts_code', 'name']:
                data_frame.loc[i, key] = getattr(stock_basic, key)

            stock_company = main_session.query(models.StockCompanyPro).filter(models.StockCompanyPro.ts_code == stock_basic.ts_code).first()
            if stock_company:
                for key in ['main_business', 'business_scope']:
                    data_frame.loc[i, key] = getattr(stock_company, key)
        except Exception as e:
            print('excetion in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### {i} #####'.format(i=i))

    file_name = '../../logs/@StockCompany.csv'
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)
    return data_frame


if __name__ == '__main__':
    main()