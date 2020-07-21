# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import midas.core.analyzer.api as api

import midas.core.data.models as models
from midas.core.data.engine import main_session
import midas.bin.env as env

COL_LASTPRICE = 'COL_LASTPRICE'
COL_DAILY_LOCAL_MAX = 'COL_DAILY_LOCAL_MAX'
COL_LOCAL_LIMIT_COUNT_2 = 'COL_LOCAL_LIMIT_COUNT_2'
COL_LOCAL_LIMIT_COUNT_10 = 'COL_LOCAL_LIMIT_COUNT_10'
COL_CIRC_MV = 'COL_CIRC_MV'

sampling_count = 200


def main(offset=0):
    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    LAST_MARKET_DATE = daily001[offset].trade_date

    data_frame = DataFrame()
    for i, stock_basic in enumerate(main_session.query(models.StockBasicPro).all()):
        try:
            for key in models.StockBasicPro.keys:
                data_frame.loc[i, key] = str(getattr(stock_basic, key))

            daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == stock_basic.ts_code,
                                                               models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(
                models.DailyPro.trade_date.desc()).limit(sampling_count).all()
            data_frame.loc[i, COL_LASTPRICE] = daily[0].close
            data_frame.loc[i, COL_DAILY_LOCAL_MAX] = api.daily_local_max(daily, local_scale=30)
            data_frame.loc[i, COL_LOCAL_LIMIT_COUNT_2] = api.local_limit_count(daily, local_scale=2)
            data_frame.loc[i, COL_LOCAL_LIMIT_COUNT_10] = api.local_limit_count(daily, local_scale=10)

            daily_basic = main_session.query(models.DailyBasic).filter(models.DailyBasic.ts_code == stock_basic.ts_code).one()
            data_frame.loc[i, COL_CIRC_MV] = daily_basic.circ_mv

        except Exception as e:
            print('exception in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### live oneplus {i} #####'.format(i=i))

    data_frame = data_frame[
        (data_frame[COL_LOCAL_LIMIT_COUNT_2] == 1)
        & (data_frame[COL_LOCAL_LIMIT_COUNT_10] == 1)
        ]

    data_frame = data_frame.sort_values(by=COL_DAILY_LOCAL_MAX, ascending=True).reset_index(drop=True)
    # data_frame = data_frame.loc[:, ['ts_code', 'name', 'industry', COL_LASTPRICE, COL_FLOAT_HOLDERS]]

    file_name = '{data_path}/live_oneplus.csv'.format(date=LAST_MARKET_DATE, data_path=env.data_path)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)


if __name__ == '__main__':
    main(offset=0)