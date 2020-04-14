# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.core.analyzer.api as api

import midas.core.data.models as models
from midas.core.data.engine import main_session
import midas.bin.env as env


def main(offset=0):
    pro = ts.pro_api()
    trade_dates = pro.daily(ts_code='000001.SZ').trade_date
    LAST_MARKET_DATE = trade_dates[offset]
    df_list = pro.top_list(trade_date=LAST_MARKET_DATE)
    df_list = df_list[
                     (df_list['pct_change'] > 9)
                     ]
    df_list = df_list.reset_index(drop=True)
    for i in range(len(df_list)):
        ts_code = df_list.loc[i, 'ts_code']
        df_inst = pro.top_inst(trade_date=LAST_MARKET_DATE, ts_code=ts_code)
        dic = df_inst.to_dict()
        buys = dic['buy']
        sells = dic['sell']
        total_buy = 0
        total_sell = 0
        for k, v in buys.items():
            total_buy += v
        for k, v in sells.items():
            total_sell += v
        avg = (total_buy + total_sell) / len(df_inst)

        df_list.loc[i, 'avg_buy_sell'] = round(avg, 2)

    df_list = df_list.sort_values(by='avg_buy_sell', ascending=False).reset_index(drop=True)

    file_name = '{logs_path}/{date}@Dragon_Tiger_List.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    with open(file_name, 'w', encoding='utf8') as file:
        df_list.to_csv(file)


if __name__ == '__main__':
    main(0)