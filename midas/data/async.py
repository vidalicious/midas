# -*- coding: utf-8 -*-
import json
import time

import midas.midas.data.models as models

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.api_pro as api

pro = ts.pro_api()
stock_basic = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,industry,fullname')

def main():
    pro = ts.pro_api()
    stock_basic = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,industry,fullname')

    for i in range(stock_basic):
        a_stock_basic = models.StockBasicPro(ts_code=stock_basic)
    pass

if __name__ == '__main__':
    main()