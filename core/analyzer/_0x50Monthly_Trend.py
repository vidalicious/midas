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


COL_CONTINUOUS_POSITIVE_COUNT = 'COL_CONTINUOUS_POSITIVE_COUNT'
COL_ALL_POSITIVE = 'COL_ALL_POSITIVE'
COL_CONTINUOUS_POSITIVE_AVERAGE_CHG = 'COL_CONTINUOUS_POSITIVE_AVERAGE_CHG'
COL_MAX_RETRACEMENT = 'COL_MAX_RETRACEMENT'
COL_SCORE = 'COL_SCORE'
COL_FLOAT_HOLDERS = 'COL_FLOAT_HOLDERS'
COL_HOLDERS_COUNT = 'COL_HOLDERS_COUNT'
COL_CIRC_MV = 'COL_CIRC_MV'

sampling_count = 300


def main(offset=0):
    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    LAST_MARKET_DATE = daily001[offset].trade_date

    data_frame = DataFrame()
    for i, stock_basic in enumerate(main_session.query(models.StockBasicPro).all()):
        try:
            if 'ST' in stock_basic.name or stock_basic.symbol.startswith('688'):
                continue

            for key in models.StockBasicPro.keys:
                data_frame.loc[i, key] = getattr(stock_basic, key)

            monthly = main_session.query(models.MonthlyPro).filter(models.MonthlyPro.ts_code == stock_basic.ts_code,
                                                               models.MonthlyPro.trade_date <= LAST_MARKET_DATE).order_by(
                models.MonthlyPro.trade_date.desc()).limit(sampling_count).all()

            data_frame.loc[i, COL_CONTINUOUS_POSITIVE_COUNT] = api.continuous_positive_chg_count(monthly)

            if len(monthly) == 0:
                all_positive = False
            elif len(monthly) == 1:
                all_positive = monthly[0].close > monthly[0].open
            else:
                all_positive = data_frame.loc[i, COL_CONTINUOUS_POSITIVE_COUNT] == len(monthly)

            data_frame.loc[i, COL_ALL_POSITIVE] = all_positive
            data_frame.loc[i, COL_CONTINUOUS_POSITIVE_AVERAGE_CHG] = round(api.continuous_positive_average_chg(monthly) * 100, 2)
            data_frame.loc[i, COL_MAX_RETRACEMENT] = round(api.klines_max_retracement(monthly[:int(data_frame.loc[i, COL_CONTINUOUS_POSITIVE_COUNT])]) * 100, 2)
            data_frame.loc[i, COL_SCORE] = api.klines_comfort_score(monthly[:int(data_frame.loc[i, COL_CONTINUOUS_POSITIVE_COUNT])]) # + 20 * data_frame.loc[i, COL_CONTINUOUS_POSITIVE_COUNT]

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
        print('##### monthly_trend {i} #####'.format(i=i))

    # plot_distribution(data_frame)

    data_frame = data_frame[
                            # (data_frame[COL_RECENT_LIMIT_COUNT_15] > 1)
                            # | ((data_frame[COL_RECENT_LIMIT_COUNT_15] == 1) & (data_frame[COL_RECENT_LIMIT_COUNT_3] > 0))
                            (data_frame[COL_CONTINUOUS_POSITIVE_COUNT] > 3)
                            | ((data_frame[COL_CONTINUOUS_POSITIVE_COUNT] > 2) & (data_frame[COL_CONTINUOUS_POSITIVE_AVERAGE_CHG] > 20))
                            | (data_frame[COL_ALL_POSITIVE] == True)
                           ]

    data_frame = data_frame.sort_values(by=COL_SCORE, ascending=False).reset_index(drop=True)

    file_name = '{logs_path}/{date}@Monthly_Trend.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)

    batch_size = 100
    sub = 0
    for i in range(0, len(data_frame), batch_size):
        sub_df = data_frame.iloc[i:i+batch_size, :]
        sub_df = sub_df.reset_index(drop=True)
        plot_candle_gather(data_frame=sub_df, last_date=LAST_MARKET_DATE, sub=sub, offset=i)
        sub += 1


def plot_distribution(data_frame):
    data = data_frame[[COL_CONTINUOUS_POSITIVE_COUNT]].values[:,0]

    sections = [-1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100]
    group_names = ['0~1', '1~2', '2~3', '3~4', '4~5', '5~6', '6~7', '7~8', '8~9', '9~10', '10~100']
    cuts = pd.cut(data, sections, labels=group_names)
    cuts.value_counts().plot(kind='bar')


def plot_candle_gather(data_frame, last_date, sub, offset):
    columns = 2
    rows = len(data_frame)

    fig = plt.figure(figsize=(columns * 15, rows * 5))
    for i in range(len(data_frame)):
        ts_code = data_frame.loc[i, 'ts_code']
        name = data_frame.loc[i, 'name']
        ax = fig.add_subplot(rows, columns, 2 * i + 1)
        misc = {
            'index': i + offset,
            COL_HOLDERS_COUNT: data_frame.loc[i, COL_HOLDERS_COUNT] if not np.isnan(data_frame.loc[i, COL_HOLDERS_COUNT]) else 0,
            COL_CIRC_MV: data_frame.loc[i, COL_CIRC_MV] if not np.isnan(data_frame.loc[i, COL_CIRC_MV]) else 0,
            COL_CONTINUOUS_POSITIVE_COUNT: data_frame.loc[i, COL_CONTINUOUS_POSITIVE_COUNT],
            COL_CONTINUOUS_POSITIVE_AVERAGE_CHG: data_frame.loc[i, COL_CONTINUOUS_POSITIVE_AVERAGE_CHG],
            COL_MAX_RETRACEMENT: data_frame.loc[i, COL_MAX_RETRACEMENT],
            COL_SCORE: data_frame.loc[i, COL_SCORE]
        }
        plot_candle_month(ax=ax, ts_code=ts_code, name=name, last_date=last_date, misc=misc)

        ax = fig.add_subplot(rows, columns, 2 * i + 2)
        plot_candle_daily(ax=ax, ts_code=ts_code, name=name, last_date=last_date, misc=misc)

    plt.tight_layout()
    plt.savefig('../../buffer/monthly_trend/{date}_monthly_trend_{sub}.png'.format(date=last_date, sub=sub))

def plot_candle_month(ax, ts_code, name, last_date, misc):
    monthly = main_session.query(models.MonthlyPro).filter(models.MonthlyPro.ts_code == ts_code,
                                                       models.MonthlyPro.trade_date <= last_date).order_by(
        models.MonthlyPro.trade_date.desc()).limit(sampling_count).all()

    df = DataFrame()
    for i, item in enumerate(monthly[300::-1]):
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

    plt.title('{index} {ts_code} {name} circ_mv:{circ_mv}亿 holders:{holders_count} continuous:{continuous} average_chg:{average_chg} retracement:{retracement} score:{score}'.format(index=int(misc['index']), ts_code=ts_code, name=name,
              circ_mv=int(misc[COL_CIRC_MV]), holders_count=int(misc[COL_HOLDERS_COUNT]), continuous=int(misc[COL_CONTINUOUS_POSITIVE_COUNT]),
              average_chg=misc[COL_CONTINUOUS_POSITIVE_AVERAGE_CHG], retracement=misc[COL_MAX_RETRACEMENT], score=misc[COL_SCORE]),
              fontproperties='Heiti TC')
    mpf.candlestick2_ochl(ax, df['open'], df['close'], df['high'], df['low'],
                          width=0.5, colorup='red', colordown='green',
                          alpha=0.5)
    # plt.grid()
    print('plot {ts_code} {name}'.format(ts_code=ts_code, name=name))


def plot_candle_daily(ax, ts_code, name, last_date, misc):
    daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == ts_code,
                                                       models.DailyPro.trade_date <= last_date).order_by(
        models.DailyPro.trade_date.desc()).limit(sampling_count).all()

    df = DataFrame()
    for i, item in enumerate(daily[300::-1]):
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

    # plt.title('{ts_code} {name} circ_mv:{circ_mv}亿 holders:{holders_count} continuous:{continuous} average_chg:{average_chg} retracement:{retracement} score:{score}'.format(ts_code=ts_code, name=name,
    #           circ_mv=int(misc[COL_CIRC_MV]), holders_count=int(misc[COL_HOLDERS_COUNT]), continuous=int(misc[COL_CONTINUOUS_POSITIVE_COUNT]),
    #           average_chg=misc[COL_CONTINUOUS_POSITIVE_AVERAGE_CHG], retracement=misc[COL_MAX_RETRACEMENT], score=misc[COL_SCORE]),
    #           fontproperties='Heiti TC')
    mpf.candlestick2_ochl(ax, df['open'], df['close'], df['high'], df['low'],
                          width=0.5, colorup='red', colordown='green',
                          alpha=0.5)
    # plt.grid()
    print('plot {ts_code} {name}'.format(ts_code=ts_code, name=name))


if __name__ == '__main__':
    main(offset=0)