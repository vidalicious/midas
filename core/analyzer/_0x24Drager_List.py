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


def main(offset=0, date=None):
    pro = ts.pro_api()
    if date:
        LAST_MARKET_DATE = date
    else:
        trade_dates = pro.daily(ts_code='000001.SZ').trade_date
        LAST_MARKET_DATE = trade_dates[offset]
    df_list = pro.top_list(trade_date=LAST_MARKET_DATE)
    df_list = df_list[
                     (df_list['pct_change'] > 9)
                     & (df_list['net_rate'] > 0)
                     ]
    df_list = df_list.reset_index(drop=True)
    for i in range(len(df_list)):
        # ts_code = df_list.loc[i, 'ts_code']
        # df_inst = pro.top_inst(trade_date=LAST_MARKET_DATE, ts_code=ts_code)
        # dic = df_inst.to_dict()
        # buys = dic['buy']
        # sells = dic['sell']
        # total_buy = 0
        # total_sell = 0
        # for k, v in buys.items():
        #     total_buy += v
        # for k, v in sells.items():
        #     total_sell += v
        # avg = (total_buy - total_sell) / len(df_inst)
        buy_sell_rate = (df_list.loc[i, 'l_buy'] - df_list.loc[i, 'l_sell']) / df_list.loc[i, 'l_sell']
        df_list.loc[i, 'buy_sell_rate'] = round(buy_sell_rate, 2)
        df_list.loc[i, 'net_amount'] = int(df_list.loc[i, 'net_amount'])
        df_list.loc[i, 'float_values'] = int(df_list.loc[i, 'float_values'])
        df_list.loc[i, 'amount_in_values'] = round(df_list.loc[i, 'net_amount'] / df_list.loc[i, 'float_values'], 2)

    df_list = df_list.sort_values(by='float_values', ascending=True).reset_index(drop=True)
    df_list = df_list.loc[:, ['trade_date', 'ts_code', 'name', 'close', 'pct_change', 'net_amount', 'amount_rate', 'float_values', 'reason', 'buy_sell_rate', 'amount_in_values']]

    file_name = '{logs_path}/{date}@Drager_List.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    with open(file_name, 'w', encoding='utf8') as file:
        df_list.to_csv(file)


if __name__ == '__main__':
    # for i in range(5):
    #     main(offset=i)
    # main(date='20191025')
    main(offset=0)