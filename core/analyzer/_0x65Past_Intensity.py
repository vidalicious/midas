# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import midas.core.analyzer.api as api

import midas.core.data.models as models
from midas.core.data.engine import main_session
import midas.bin.env as env

COL_PAST_INTENSITY = 'COL_PAST_INTENSITY'

sampling_count = 200

def get_intensity(chg):
    if chg > 9:
        intensity = 4
    elif chg > 6:
        intensity = 3
    elif chg > 3:
        intensity = 2
    elif chg > 0:
        intensity = 1
    elif chg > -3:
        intensity = -1
    elif chg > -6:
        intensity = -2
    elif chg > -9:
        intensity = -3
    else:
        intensity = -4

    return intensity

def get_past_intensity(daily):
    if not daily:
        return 0

    past_intensity = 0
    is_positive = daily[0].pct_chg > 0
    for item in daily:
        chg = item.pct_chg
        intensity = get_intensity(chg)
        if is_positive and intensity < 0:
            break
        if (not is_positive) and intensity > 0:
            break
        past_intensity += intensity
    return past_intensity

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
            data_frame.loc[i, COL_PAST_INTENSITY] = get_past_intensity(daily)

        except Exception as e:
            print('exception in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### past intensity {i} #####'.format(i=i))

    # data_frame = data_frame[
    #     (data_frame[COL_PAST_INTENSITY] < 0)
    #     ]
    #
    # data_frame = data_frame.sort_values(by=COL_DAILY_LOCAL_MAX, ascending=True).reset_index(drop=True)
    # data_frame = data_frame.loc[:, ['ts_code', 'name', 'industry', COL_LASTPRICE, COL_FLOAT_HOLDERS]]

    file_name = '{data_path}/past_intensity.csv'.format(date=LAST_MARKET_DATE, data_path=env.data_path)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)


if __name__ == '__main__':
    main(offset=0)