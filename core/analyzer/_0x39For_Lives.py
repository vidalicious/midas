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
COL_ACCUMULATION_AGGRESSIVE = 'COL_ACCUMULATION_AGGRESSIVE'
COL_UP_RANGE = 'COL_UP_RANGE'

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
            data_frame.loc[i, COL_ACCUMULATION_AGGRESSIVE] = api.aggressive_chg_accumulation(daily[:10])

        except Exception as e:
            print('exception in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### for lives {i} #####'.format(i=i))

    # data_frame = data_frame[
    #     (data_frame[COL_DAILY_SILENT] == True)
    #     & (data_frame[COL_UP_RANGE] < 0.2)
    #     ]

    data_frame = data_frame.sort_values(by=COL_DAILY_LOCAL_MAX, ascending=True).reset_index(drop=True)
    # data_frame = data_frame.loc[:, ['ts_code', 'name', 'industry', COL_LASTPRICE, COL_FLOAT_HOLDERS]]

    file_name = '{data_path}/for_lives.csv'.format(date=LAST_MARKET_DATE, data_path=env.data_path)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)


if __name__ == '__main__':
    main(offset=0)