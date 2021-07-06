# -*- coding: utf-8 -*-
import json
import time
import math
import tushare as ts
import talib
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
import mpl_finance as mpf

COL_CHG = 'COL_CHG'
COL_PROBABILITY = 'COL_PROBABILITY'
COL_RECENT_HALF_PROBABILITY = 'COL_RECENT_HALF_PROBABILITY'
COL_PROBABILITY_DIFFER = 'COL_PROBABILITY_DIFFER'
COL_FLOAT_HOLDERS = 'COL_FLOAT_HOLDERS'
COL_HOLDERS_COUNT = 'COL_HOLDERS_COUNT'
COL_CIRC_MV = 'COL_CIRC_MV'

sampling_count = 300
WINDOW_WIDTH = 10
probability_map = dict()

# tmp_weights = [(WINDOW_WIDTH - i) ** 2 for i in range(WINDOW_WIDTH)]
# tmp_weights_sum = sum(tmp_weights)
# weights = [i / tmp_weights_sum for i in tmp_weights]

# def get_probability(sequence, window_width, local_scale):
#     sequence = sequence[:window_width + local_scale]
#     chgs = [i.pct_chg for i in sequence]
#
#     if len(chgs) < window_width:
#         return [np.mean(chgs)]
#
#     res = []
#     for i in range(local_scale):
#         try:
#             probability = 0
#             for j in range(window_width):
#                 chg = chgs[i + j]
#                 probability += chg / window_width
#
#             res.append(probability)
#         except Exception as e:
#             break
#
#     return res

def get_probability(sequence, window_width):
    sequence = sequence[:window_width]
    chgs = [i.pct_chg for i in sequence]
    return np.mean(chgs)


def accumulate(sequence):
    res = 0
    for item in sequence:
        if item > 0:
            res += item
        else:
            break
    return res


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

            daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == stock_basic.ts_code,
                                                               models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(
                models.DailyPro.trade_date.desc()).limit(sampling_count).all()

            sub_daily = daily[1:10]
            daily_closes = [i.close for i in sub_daily]
            min_close = min(daily_closes)

            data_frame.loc[i, COL_CHG] = round((daily[0].close / min_close - 1) * 100, 2)

            probability = get_probability(sequence=daily, window_width=WINDOW_WIDTH)
            recent_half_probability = get_probability(sequence=daily, window_width=int(WINDOW_WIDTH / 2))
            # probability_map[stock_basic.ts_code] = probability
            data_frame.loc[i, COL_PROBABILITY] = round(probability, 2)
            data_frame.loc[i, COL_RECENT_HALF_PROBABILITY] = round(recent_half_probability, 2)
            data_frame.loc[i, COL_PROBABILITY_DIFFER] = round(recent_half_probability - probability, 2)

            daily_basic = main_session.query(models.DailyBasic).filter(models.DailyBasic.ts_code == stock_basic.ts_code).one()
            data_frame.loc[i, COL_CIRC_MV] = daily_basic.circ_mv

            # holders = main_session.query(models.FloatHolderPro).filter(models.FloatHolderPro.ts_code == stock_basic.ts_code).all()
            # h_set = set()
            # for item in holders:
            #     h_set.add(item.holder_name)
            # data_frame.loc[i, COL_FLOAT_HOLDERS] = '\n'.join(h_set)
            # data_frame.loc[i, COL_HOLDERS_COUNT] = len(h_set)

        except Exception as e:
            print('exception in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### window_probability {i} #####'.format(i=i))

    data_frame = data_frame[
                            (data_frame[COL_PROBABILITY] > 1)
                           ]

    data_frame = data_frame.sort_values(by=COL_PROBABILITY, ascending=False).reset_index(drop=True)
    # data_frame = data_frame.head(300)

    file_name = '{logs_path}/{date}@Window_Probability.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)

    # 100 * 2 * 5 * 100 = 100000
    batch_size = int(65000 / 100 / 5) #100
    sub = 0
    for i in range(0, len(data_frame), batch_size):
        sub_df = data_frame.iloc[i:i+batch_size, :]
        sub_df = sub_df.reset_index(drop=True)
        plot_candle_gather(data_frame=sub_df, last_date=LAST_MARKET_DATE, sub=sub, offset=i)
        sub += 1


def plot_candle_gather(data_frame, last_date, sub, offset):
    columns = 1
    rows = len(data_frame)

    # columns = 2
    # rows = len(data_frame)

    fig = plt.figure(figsize=(columns * 15, rows * 5))#/ 2))
    for i in range(len(data_frame)):
        ts_code = data_frame.loc[i, 'ts_code']
        name = data_frame.loc[i, 'name']
        ax = fig.add_subplot(rows, columns, i + 1)
        misc = {
            'index': i + offset,
            # COL_HOLDERS_COUNT: data_frame.loc[i, COL_HOLDERS_COUNT] if not np.isnan(data_frame.loc[i, COL_HOLDERS_COUNT]) else 0,
            COL_CIRC_MV: data_frame.loc[i, COL_CIRC_MV] if not np.isnan(data_frame.loc[i, COL_CIRC_MV]) else 0,
            COL_CHG: round(data_frame.loc[i, COL_CHG], 2),
            COL_PROBABILITY: round(data_frame.loc[i, COL_PROBABILITY], 2)
        }
        # plot_candle_month(ax=ax, ts_code=ts_code, name=name, last_date=last_date, misc=misc)
        plot_candle_daily(ax=ax, ts_code=ts_code, name=name, last_date=last_date, misc=misc)
        # ax = fig.add_subplot(rows, columns, 2 * i + 2)
        # plot_stuff_daily(ax=ax, ts_code=ts_code, last_date=last_date, misc=misc)

    plt.tight_layout()
    plt.savefig('../../buffer/window_probability/{date}_window_probability_{sub}.png'.format(date=last_date, sub=sub))

def plot_candle_month(ax, ts_code, name, last_date, misc):
    monthly = main_session.query(models.MonthlyPro).filter(models.MonthlyPro.ts_code == ts_code,
                                                       models.MonthlyPro.trade_date <= last_date).order_by(
        models.MonthlyPro.trade_date.desc()).limit(sampling_count).all()

    if monthly:
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

        mpf.candlestick2_ochl(ax, df['open'], df['close'], df['high'], df['low'],
                              width=0.5, colorup='red', colordown='green',
                              alpha=0.5)

    plt.title('{index} {ts_code} {name} circ_mv:{circ_mv}亿'.format(index=int(misc['index']), ts_code=ts_code, name=name,
                                                                    circ_mv=int(misc[COL_CIRC_MV])),
              fontproperties='Heiti TC')

    # plt.grid()
    print('plot {ts_code} {name}'.format(ts_code=ts_code, name=name))


def plot_stuff_daily(ax, ts_code, last_date, misc):
    probability = probability_map[ts_code]

    daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == ts_code,
                                                       models.DailyPro.trade_date <= last_date).order_by(
        models.DailyPro.trade_date.desc()).limit(sampling_count).all()
    probability = probability[::-1]
    df = DataFrame()
    for i, item in enumerate(daily[len(probability) - 1::-1]):
        df.loc[i, 'date'] = str(item.trade_date)
        df.loc[i, 'probability'] = probability[i]

    ax.set_xticks(range(0, len(df['date']), 20))
    ax.set_xticklabels(df['date'][::20])

    sns.lineplot(data=df, x='date', y='probability', lw=1)
    plt.axhline(y=0, c='r', ls='--', lw=1)
    plt.title('probability:{probability}'.format(probability=misc[COL_PROBABILITY]),
              fontproperties='Heiti TC')


def plot_candle_daily(ax, ts_code, name, last_date, misc):
    probability = probability_map[ts_code]

    daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == ts_code,
                                                       models.DailyPro.trade_date <= last_date).order_by(
        models.DailyPro.trade_date.desc()).limit(sampling_count).all()

    df = DataFrame()
    for i, item in enumerate(daily[len(probability) - 1::-1]):
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

    mpf.candlestick2_ochl(ax, df['open'], df['close'], df['high'], df['low'],
                          width=0.5, colorup='red', colordown='green',
                          alpha=0.5)

    plt.title('{index} {ts_code} {name} circ_mv:{circ_mv}亿 chg:{chg} probability:{probability}'.format(index=int(misc['index']), ts_code=ts_code, name=name,
        circ_mv=int(misc[COL_CIRC_MV]), chg=misc[COL_CHG], probability=misc[COL_PROBABILITY]),
        fontproperties='Heiti TC')
    # plt.grid()
    print('plot {ts_code} {name}'.format(ts_code=ts_code, name=name))


if __name__ == '__main__':
    main(offset=0)