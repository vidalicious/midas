# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.api_pro as api
import midas.midas.data.models as models
from midas.midas.data.engine import main_session


def main():
    pro = ts.pro_api()
    main_session.query(models.StockCompanyPro).delete()
    main_session.commit()
    for exchange in ['SZSE', 'SSE']:
        df = pro.stock_company(exchange=exchange, fields='ts_code,main_business,business_scope')
        for i in range(len(df)):
            a_stock_company = models.StockCompanyPro(ts_code=df.loc[i, 'ts_code'],
                                                     main_business=df.loc[i, 'main_business'],
                                                     business_scope=df.loc[i, 'business_scope']
                                                    )
            main_session.add(a_stock_company)
        main_session.commit()

    print('##### async stock company finished #####')


if __name__ == '__main__':
    main()


