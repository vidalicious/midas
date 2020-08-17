# -*- coding: utf-8 -*-
import json
import time
import math
import tushare as ts
import talib
from pandas import DataFrame
import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd
import midas.core.analyzer.api as api

import midas.core.data.models as models
from midas.core.data.engine import main_session
import midas.bin.env as env
import mpl_finance as mpf


COL_LASTPRICE = 'COL_LASTPRICE'
COL_RECENT_LIMIT_COUNT_15 = 'COL_RECENT_LIMIT_COUNT_15'
COL_RECENT_LIMIT_COUNT_3 = 'COL_RECENT_LIMIT_COUNT_3'
COL_FLOAT_HOLDERS = 'COL_FLOAT_HOLDERS'
COL_HOLDERS_COUNT = 'COL_HOLDERS_COUNT'
COL_CIRC_MV = 'COL_CIRC_MV'

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
            data_frame.loc[i, COL_RECENT_LIMIT_COUNT_15] = api.local_limit_count(daily, local_scale=15)
            data_frame.loc[i, COL_RECENT_LIMIT_COUNT_3] = api.local_limit_count(daily, local_scale=3)

            daily_basic = main_session.query(models.DailyBasic).filter(models.DailyBasic.ts_code == stock_basic.ts_code).one()
            data_frame.loc[i, COL_CIRC_MV] = daily_basic.circ_mv

            holders = main_session.query(models.FloatHolderPro).filter(models.FloatHolderPro.ts_code == stock_basic.ts_code).all()
            h_set = set()
            for item in holders:
                h_set.add(item.holder_name)
            data_frame.loc[i, COL_FLOAT_HOLDERS] = '\n'.join(h_set)
            data_frame.loc[i, COL_HOLDERS_COUNT] = len(h_set)

        except Exception as e:
            print('exception in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### limit_rank {i} #####'.format(i=i))

    data_frame = data_frame[
                            (data_frame[COL_RECENT_LIMIT_COUNT_15] > 1)
                            | ((data_frame[COL_RECENT_LIMIT_COUNT_15] == 1) & (data_frame[COL_RECENT_LIMIT_COUNT_3] > 0))
                           ]

    data_frame = data_frame.sort_values(by=COL_RECENT_LIMIT_COUNT_15, ascending=False).reset_index(drop=True)
    # data_frame = data_frame.loc[:, ['ts_code', 'name', 'industry', COL_LASTPRICE, COL_FLOAT_HOLDERS]]

    file_name = '{logs_path}/{date}@Limit_Rank.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)

    batch_size = 500
    sub = 0
    for i in range(0, len(data_frame), batch_size):
        sub_df = data_frame.iloc[i:i+batch_size, :]
        sub_df = sub_df.reset_index(drop=True)
        plot_candle_gather(data_frame=sub_df, last_date=LAST_MARKET_DATE, sub=sub)
        sub += 1


def plot_candle_gather(data_frame, last_date, sub):
    columns = 3
    rows = math.ceil(len(data_frame) / columns)

    fig = plt.figure(figsize=(columns * 5, rows * 5 / 2))
    for i in range(len(data_frame)):
        ts_code = data_frame.loc[i, 'ts_code']
        name = data_frame.loc[i, 'name']
        ax = fig.add_subplot(rows, columns, i + 1)
        misc = {
            COL_HOLDERS_COUNT: data_frame.loc[i, COL_HOLDERS_COUNT] if not np.isnan(data_frame.loc[i, COL_HOLDERS_COUNT]) else 0,
            COL_CIRC_MV: data_frame.loc[i, COL_CIRC_MV] if not np.isnan(data_frame.loc[i, COL_CIRC_MV]) else 0,
            COL_RECENT_LIMIT_COUNT_15: data_frame.loc[i, COL_RECENT_LIMIT_COUNT_15]
        }
        plot_candle(ax=ax, ts_code=ts_code, name=name, last_date=last_date, misc=misc)

    plt.tight_layout()
    plt.savefig('../../buffer/limit_rank/{date}_limit_rank_{sub}.png'.format(date=last_date, sub=sub))

def plot_candle(ax, ts_code, name, last_date, misc):
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

    sma_5 = talib.SMA(np.array(df['close']), 5)
    sma_10 = talib.SMA(np.array(df['close']), 10)
    sma_20 = talib.SMA(np.array(df['close']), 20)

    ax.set_xticks(range(0, len(df['date']), 20))
    ax.set_xticklabels(df['date'][::20])
    ax.plot(sma_5, linewidth=1, label='ma5')
    ax.plot(sma_10, linewidth=1, label='ma10')
    ax.plot(sma_20, linewidth=1, label='ma20')

    plt.title('{ts_code} {name} circ_mv:{circ_mv}亿 holders:{holders_count} limits:{limits_count}'.format(ts_code=ts_code, name=name,
              circ_mv=int(misc[COL_CIRC_MV]), holders_count=int(misc[COL_HOLDERS_COUNT]), limits_count=int(misc[COL_RECENT_LIMIT_COUNT_15])),
              fontproperties='Heiti TC')
    mpf.candlestick2_ochl(ax, df['open'], df['close'], df['high'], df['low'],
                          width=0.5, colorup='red', colordown='green',
                          alpha=0.5)
    # plt.grid()
    print('plot {ts_code} {name}'.format(ts_code=ts_code, name=name))


if __name__ == '__main__':
    main(offset=0)