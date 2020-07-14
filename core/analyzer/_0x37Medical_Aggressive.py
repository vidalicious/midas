# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np
import math
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import midas.core.analyzer.api as api

import midas.core.data.models as models
from midas.core.data.engine import main_session
import midas.bin.env as env
import shutil
import os
import mpl_finance as mpf


COL_DAILY_BREAK = 'COL_DAILY_BREAK'
COL_RECENT_AGGRESSIVE = 'COL_RECENT_AGGRESSIVE'
COL_IS_MEDICAL = 'COL_IS_MEDICAL'
COL_LASTPRICE = 'COL_LASTPRICE'
COL_UP_RANGE = 'COL_UP_RANGE'
COL_FLOAT_HOLDERS = 'COL_FLOAT_HOLDERS'
COL_HOLDERS_COUNT = 'COL_HOLDERS_COUNT'

sampling_count = 200


def main(offset=0):
    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    LAST_MARKET_DATE = daily001[offset].trade_date

    data_frame = DataFrame()
    for i, stock_basic in enumerate(main_session.query(models.StockBasicPro).all()):
        try:
            for key in models.StockBasicPro.keys:
                data_frame.loc[i, key] = getattr(stock_basic, key)

            data_frame.loc[i, COL_IS_MEDICAL] = api.is_medical(stock_basic.industry)

            daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == stock_basic.ts_code,
                                                               models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(
                models.DailyPro.trade_date.desc()).limit(sampling_count).all()
            data_frame.loc[i, COL_LASTPRICE] = daily[0].close
            data_frame.loc[i, COL_DAILY_BREAK] = api.daily_break(daily, local_scale=60)
            data_frame.loc[i, COL_RECENT_AGGRESSIVE] = api.recent_limit(daily)

            daily_local_min = api.daily_local_min(sequence=daily, local_scale=10)
            data_frame.loc[i, COL_UP_RANGE] = round((daily[0].close / daily_local_min) - 1, 2)

            holders = main_session.query(models.FloatHolderPro).filter(models.FloatHolderPro.ts_code == stock_basic.ts_code).all()
            h_set = set()
            for item in holders:
                h_set.add(item.holder_name)
            data_frame.loc[i, COL_FLOAT_HOLDERS] = '\n'.join(h_set)
            data_frame.loc[i, COL_HOLDERS_COUNT] = len(h_set)

        except Exception as e:
            print('exception in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### medical aggressive {i} #####'.format(i=i))

    data_frame = data_frame[
                            (data_frame[COL_DAILY_BREAK] == True)
                            & (data_frame[COL_RECENT_AGGRESSIVE] == True)
                            & (data_frame[COL_IS_MEDICAL] == True)
                           ]

    data_frame = data_frame.sort_values(by=COL_UP_RANGE, ascending=True).reset_index(drop=True)
    # data_frame = data_frame.loc[:, ['ts_code', 'name', 'industry', COL_LASTPRICE, COL_FLOAT_HOLDERS]]

    file_name = '{logs_path}/{date}@Medical_Aggressive.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)

    plot_candle_gather(data_frame=data_frame, last_date=LAST_MARKET_DATE)


def plot_candle_gather(data_frame, last_date):
    columns = 3
    rows = math.ceil(len(data_frame) / columns)

    fig = plt.figure(figsize=(columns * 5, rows * 5 / 2))
    for i in range(len(data_frame)):
        ts_code = data_frame.loc[i, 'ts_code']
        name = data_frame.loc[i, 'name']
        ax = fig.add_subplot(rows, columns, i + 1)
        plot_candle(ax=ax, ts_code=ts_code, name=name, last_date=last_date, holders_count=data_frame.loc[i, COL_HOLDERS_COUNT])

    plt.tight_layout()
    plt.savefig('../../buffer/medical_aggressive/{date}_medical_aggressive.png'.format(date=last_date))

def plot_candle(ax, ts_code, name, last_date, holders_count):
    daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == ts_code,
                                                       models.DailyPro.trade_date <= last_date).order_by(
        models.DailyPro.trade_date.desc()).limit(sampling_count).all()

    df = DataFrame()
    for i, item in enumerate(daily[60::-1]):
        df.loc[i, 'date'] = str(item.trade_date)
        df.loc[i, 'open'] = item.open
        df.loc[i, 'close'] = item.close
        df.loc[i, 'high'] = item.high
        df.loc[i, 'low'] = item.low

    ax.set_xticks(range(0, len(df['date']), 20))
    ax.set_xticklabels(df['date'][::20])

    plt.title('{ts_code} {name} holders: {holders_count}'.format(ts_code=ts_code, name=name, holders_count=int(holders_count)),
              fontproperties='Heiti TC')
    mpf.candlestick2_ochl(ax, df['open'], df['close'], df['high'], df['low'],
                          width=0.5, colorup='red', colordown='green',
                          alpha=0.5)
    # plt.grid()
    print('plot {ts_code} {name}'.format(ts_code=ts_code, name=name))


if __name__ == '__main__':
    main(offset=0)