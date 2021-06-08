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
from bs4 import BeautifulSoup

COL_CHG = 'COL_CHG'
COL_ODDS = 'COL_ODDS'
COL_DELTA_ODDS = 'COL_DELTA_ODDS'
# COL_MA_20_SLOPE = 'COL_MA_20_SLOPE'
COL_FLOAT_HOLDERS = 'COL_FLOAT_HOLDERS'
COL_HOLDERS_COUNT = 'COL_HOLDERS_COUNT'
COL_CIRC_MV = 'COL_CIRC_MV'

sampling_count = 300
WINDOW_WIDTH = 10
window_odds_map = dict()

tmp_weights = [(WINDOW_WIDTH - i) ** 2 for i in range(WINDOW_WIDTH)]
tmp_weights_sum = sum(tmp_weights)
weights = [i / tmp_weights_sum for i in tmp_weights]

def get_window_odds(sequence, window_width, local_scale):
    if len(sequence) < window_width:
        return []

    sequence = sequence[:window_width + local_scale]
    chgs = [i.pct_chg for i in sequence]

    odds = []
    for i in range(local_scale):
        try:
            weighted_chgs = 0
            for j in range(window_width):
                weighted_chgs += chgs[i + j] * weights[j]

            odds.append(weighted_chgs)
        except Exception as e:
            break

    return odds

def get_delta_odds(odds):
    delta_odds = 0
    for i in range(len(odds) - 1):
        if odds[i] < odds[i+1]:
            delta_odds += odds[i] - odds[i+1]
        else:
            break

    return delta_odds


def daily_close_ma(daily=None, step=5):
    if len(daily) < step:
        raise Exception('invalid daily data')

    closes = list()
    for item in daily:
        closes.append(item.close)

    result = list()
    for i in range(len(daily) - step + 1):
        ma = round(np.mean(closes[i:i + step]), 2)
        result.append(ma)

    return result


def get_kaipanla_symbols(concept):
    with open('{data_path}/{concept}.html'.format(data_path=env.data_path, concept=concept), "r") as f:  # 打开文件
        text = f.read()  # 读取文
    soup = BeautifulSoup(markup=text, features='lxml')
    symbol_tags = soup.find_all(class_='c gray')

    symbols = []
    for tag in symbol_tags:
        symbol = tag.get_text()
        symbols.append(symbol)

    return symbols


def get_symbols():
    symbol_set = set()
    for concept in ['锂电池', '酿酒', '芯片', '华为']:
        symbols = get_kaipanla_symbols(concept=concept)
        for symbol in symbols:
            symbol_set.add(symbol)

    return list(symbol_set)


def main(offset=0):
    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    LAST_MARKET_DATE = daily001[offset].trade_date

    target_symbols = get_symbols()

    data_frame = DataFrame()
    for i, stock_basic in enumerate(main_session.query(models.StockBasicPro).all()):
        try:
            if 'ST' in stock_basic.name or stock_basic.symbol.startswith('688'):
                continue

            if stock_basic.symbol not in target_symbols:
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

            window_odds = get_window_odds(sequence=daily, window_width=WINDOW_WIDTH, local_scale=300-WINDOW_WIDTH)
            # accumulate_odds = accumulate_positive_odds(window_odds)
            window_odds_map[stock_basic.ts_code] = window_odds
            # data_frame.loc[i, COL_ACCUMULATE_ODDS] = accumulate_odds
            data_frame.loc[i, COL_ODDS] = round(window_odds[0], 2)
            data_frame.loc[i, COL_DELTA_ODDS] = get_delta_odds(window_odds) #round(window_odds[0] - window_odds[1], 2)

            # ma_20 = daily_close_ma(daily=daily, step=20)
            # data_frame.loc[i, COL_MA_20_SLOPE] = round((ma_20[0] / ma_20[1] - 1) * 100, 2)

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
        print('##### window_odds {i} #####'.format(i=i))

    data_frame = data_frame[
                            # (data_frame[COL_MA_20_SLOPE] > 0)
                            (data_frame[COL_DELTA_ODDS] < 0)
                           ]

    data_frame = data_frame.sort_values(by=COL_DELTA_ODDS, ascending=True).reset_index(drop=True)
    # data_frame = data_frame.head(100)

    file_name = '{data_path}/window_odds.csv'.format(date=LAST_MARKET_DATE, data_path=env.data_path)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)

    file_name = '{logs_path}/{date}@Window_Odds.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)

    file_name = '{logs_path}/{date}@Window_Odds_Targets'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    targets = []
    for i in range(0, len(data_frame)):
        targets.append('\'{}\''.format(data_frame.loc[i, 'symbol']))
    with open(file_name, 'w', encoding='utf8') as file:
        file.write(',\n'.join(targets))

    batch_size = 100
    sub = 0
    for i in range(0, len(data_frame), batch_size):
        sub_df = data_frame.iloc[i:i+batch_size, :]
        sub_df = sub_df.reset_index(drop=True)
        plot_candle_gather(data_frame=sub_df, last_date=LAST_MARKET_DATE, sub=sub, offset=i)
        sub += 1


def plot_candle_gather(data_frame, last_date, sub, offset):
    columns = 1
    rows = len(data_frame) * 2

    fig = plt.figure(figsize=(columns * 15, rows * 5 / 2))
    for i in range(len(data_frame)):
        ts_code = data_frame.loc[i, 'ts_code']
        name = data_frame.loc[i, 'name']
        ax = fig.add_subplot(rows, columns, 2 * i + 1)
        misc = {
            'index': i + offset,
            # COL_HOLDERS_COUNT: data_frame.loc[i, COL_HOLDERS_COUNT] if not np.isnan(data_frame.loc[i, COL_HOLDERS_COUNT]) else 0,
            COL_CIRC_MV: data_frame.loc[i, COL_CIRC_MV] if not np.isnan(data_frame.loc[i, COL_CIRC_MV]) else 0,
            COL_ODDS: data_frame.loc[i, COL_ODDS],
            COL_DELTA_ODDS : data_frame.loc[i, COL_DELTA_ODDS],
            COL_CHG: data_frame.loc[i, COL_CHG]
        }
        # plot_candle_month(ax=ax, ts_code=ts_code, name=name, last_date=last_date, misc=misc)
        plot_candle_daily(ax=ax, ts_code=ts_code, name=name, last_date=last_date, misc=misc)
        ax = fig.add_subplot(rows, columns, 2 * i + 2)
        plot_odds_daily(ax=ax, ts_code=ts_code, last_date=last_date, misc=misc)

    plt.tight_layout()
    plt.savefig('../../buffer/window_odds/{date}_window_odds_{sub}.png'.format(date=last_date, sub=sub))

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


def plot_odds_daily(ax, ts_code, last_date, misc):
    odds = window_odds_map[ts_code]

    daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == ts_code,
                                                       models.DailyPro.trade_date <= last_date).order_by(
        models.DailyPro.trade_date.desc()).limit(sampling_count).all()
    odds = odds[::-1]
    df = DataFrame()
    for i, item in enumerate(daily[len(odds) - 1::-1]):
        df.loc[i, 'date'] = str(item.trade_date)
        df.loc[i, 'odds'] = odds[i]

    ax.set_xticks(range(0, len(df['date']), 20))
    ax.set_xticklabels(df['date'][::20])

    sns.lineplot(data=df, x='date', y='odds', lw=1)
    plt.axhline(y=0, c='r', ls='--', lw=1)
    plt.title('odds:{odds} delta_odds:{delta_odds}'.format(odds=round(misc[COL_ODDS], 2), delta_odds=round(misc[COL_DELTA_ODDS], 2)),
              fontproperties='Heiti TC')


def plot_candle_daily(ax, ts_code, name, last_date, misc):
    odds = window_odds_map[ts_code]

    daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == ts_code,
                                                       models.DailyPro.trade_date <= last_date).order_by(
        models.DailyPro.trade_date.desc()).limit(sampling_count).all()

    df = DataFrame()
    for i, item in enumerate(daily[len(odds) - 1::-1]):
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

    plt.title('{index} {ts_code} {name} circ_mv:{circ_mv}亿 chg:{chg}'.format(index=int(misc['index']), ts_code=ts_code, name=name,
                                                                    circ_mv=int(misc[COL_CIRC_MV]), chg=round(misc[COL_CHG], 2)),
              fontproperties='Heiti TC')
    # plt.grid()
    print('plot {ts_code} {name}'.format(ts_code=ts_code, name=name))


if __name__ == '__main__':
    main(offset=0)