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
COL_DAILY_SILENT = 'COL_DAILY_SILENT'
COL_DAILY_LOCAL_MAX = 'COL_DAILY_LOCAL_MAX'
COL_UP_RANGE = 'COL_UP_RANGE'

sampling_count = 200


def main(offset=0):
    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    LAST_MARKET_DATE = daily001[offset].trade_date

    data_frame = DataFrame()
    for i, stock_basic in enumerate(main_session.query(models.StockBasicPro).all()):
        try:
            for key in models.StockBasicPro.keys:
                data_frame.loc[i, key] = getattr(stock_basic, key)

            daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == stock_basic.ts_code,
                                                               models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(
                models.DailyPro.trade_date.desc()).limit(sampling_count).all()
            data_frame.loc[i, COL_LASTPRICE] = daily[0].close
            data_frame.loc[i, COL_DAILY_SILENT] = api.daily_silent(daily, local_scale=5)

            data_frame.loc[i, COL_DAILY_LOCAL_MAX] = api.daily_local_max(daily, local_scale=30)

            # daily_local_min = api.daily_local_min(sequence=daily, local_scale=30)
            # data_frame.loc[i, COL_UP_RANGE] = round((daily[0].close / daily_local_min) - 1, 2)


        except Exception as e:
            print('exception in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### silent ones {i} #####'.format(i=i))

    data_frame = data_frame[
                            (data_frame[COL_DAILY_SILENT] == True)
                            # & (data_frame[COL_UP_RANGE] < 0.2)
                           ]

    data_frame = data_frame.sort_values(by=COL_DAILY_LOCAL_MAX, ascending=True).reset_index(drop=True)
    # data_frame = data_frame.loc[:, ['ts_code', 'name', 'industry', COL_LASTPRICE, COL_FLOAT_HOLDERS]]

    file_name = '{data_path}/silent_ones'.format(data_path=env.data_path)
    with open(file_name, 'w', encoding='utf8') as file:
        res = []
        for i in range(len(data_frame)):
            name = data_frame.loc[i, 'name']
            symbol = data_frame.loc[i, 'symbol']
            market = data_frame.loc[i, 'ts_code'].split('.')[1].lower()
            daily_local_max = data_frame.loc[i, COL_DAILY_LOCAL_MAX]
            res.append('{name},{symbol},{market},{daily_local_max}'.format(name=name, symbol=symbol, market=market,
                                                                           daily_local_max=daily_local_max))
        file.write('\n'.join(res))



if __name__ == '__main__':
    main(offset=0)