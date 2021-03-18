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
COL_LAST_CHG = 'COL_LAST_CHG'
COL_DAILY_SILENT = 'COL_DAILY_SILENT'
COL_DAILY_LOCAL_MAX = 'COL_DAILY_LOCAL_MAX'
COL_HIT_LIMIT = 'COL_HIT_LIMIT'

sampling_count = 200


def main(offset=0):
    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    LAST_MARKET_DATE = daily001[offset].trade_date

    data_frame = DataFrame()
    for i, stock_basic in enumerate(main_session.query(models.StockBasicPro).all()):
        try:
            if 'ST' in stock_basic.name \
                    or stock_basic.symbol.startswith('300') \
                    or stock_basic.symbol.startswith('688'):
                continue

            for key in models.StockBasicPro.keys:
                data_frame.loc[i, key] = getattr(stock_basic, key)

            daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == stock_basic.ts_code,
                                                               models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(
                models.DailyPro.trade_date.desc()).limit(sampling_count).all()
            data_frame.loc[i, COL_LASTPRICE] = daily[0].close
            data_frame.loc[i, COL_DAILY_SILENT] = api.daily_silent(daily, local_scale=6)

            data_frame.loc[i, COL_LAST_CHG] = daily[0].pct_chg

            today_limit_price = round(daily[0].pre_close * 1.1, 2)
            today_high_price = daily[0].high

            data_frame.loc[i, COL_HIT_LIMIT] = today_limit_price == today_high_price

            # data_frame.loc[i, COL_DAILY_LOCAL_MAX] = api.daily_local_max(daily, local_scale=10)
        except Exception as e:
            print('exception in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### test {i} #####'.format(i=i))

    data_frame = data_frame[
                            (data_frame[COL_DAILY_SILENT] == True)
                            & (data_frame[COL_HIT_LIMIT] == True)
                           ]

    data_frame = data_frame.sort_values(by=COL_LAST_CHG, ascending=False).reset_index(drop=True)
    # data_frame = data_frame.loc[:, ['ts_code', 'name', 'industry', COL_LASTPRICE, COL_FLOAT_HOLDERS]]

    file_name = '{data_path}/test_first_limit_crasher.csv'.format(date=LAST_MARKET_DATE, data_path=env.data_path)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)

if __name__ == '__main__':
    main(offset=0)