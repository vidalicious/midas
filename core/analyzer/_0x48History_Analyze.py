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


COL_RECENT_LIMIT_COUNT_300 = 'COL_RECENT_LIMIT_COUNT_300'

sampling_count = 301

targets = [
    '奥特佳', '星期六', '正川股份', '振德医疗', '海汽集团', '省广集团', '蓝英装备', '容大感光', '漫步者', '道恩股份', '秀强股份',
    '宣亚国际', '新力金融', '西藏药业', '模塑科技', '中潜股份', '沈阳化工', '引力传媒', '北玻股份', '星徽精密', '凯撒旅业', '泰达股份', '掌阅科技',
    '爱司凯', '天山生物', '搜于特', '南宁百货', '银之杰', '三五互联', '保龄宝', '君正集团', '金健米业', '通光线缆', '万通智控', '联环药业',
    '凯撒文化', '奥美医疗', '光启技术', '海特生物', '智慧农业', '王府井', '光大证券'
]

def main(offset=0):
    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    LAST_MARKET_DATE = daily001[offset].trade_date

    data_frame = DataFrame()
    for i, stock_basic in enumerate(main_session.query(models.StockBasicPro).all()):
        if not stock_basic.name in targets:
            continue

        try:
            for key in models.StockBasicPro.keys:
                data_frame.loc[i, key] = getattr(stock_basic, key)

            daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == stock_basic.ts_code,
                                                               models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(
                models.DailyPro.trade_date.desc()).limit(sampling_count).all()
            data_frame.loc[i, COL_RECENT_LIMIT_COUNT_300] = api.local_limit_count(daily, local_scale=300)

        except Exception as e:
            print('exception in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### history_analyze {i} #####'.format(i=i))

    # data_frame = data_frame[
    #                         # (data_frame[COL_RECENT_LIMIT_COUNT_15] > 1)
    #                         # | ((data_frame[COL_RECENT_LIMIT_COUNT_15] == 1) & (data_frame[COL_RECENT_LIMIT_COUNT_3] > 0))
    #                         (data_frame[COL_RECENT_LIMIT_COUNT_300] > 5)
    #                        ]

    data_frame = data_frame.sort_values(by=COL_RECENT_LIMIT_COUNT_300, ascending=False).reset_index(drop=True)
    # data_frame = data_frame.loc[:, ['ts_code', 'name', 'industry', COL_LASTPRICE, COL_FLOAT_HOLDERS]]

    file_name = '{logs_path}/{date}@History_Analyze.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)

    batch_size = 200
    sub = 0
    for i in range(0, len(data_frame), batch_size):
        sub_df = data_frame.iloc[i:i+batch_size, :]
        sub_df = sub_df.reset_index(drop=True)
        plot_candle_gather(data_frame=sub_df, last_date=LAST_MARKET_DATE, sub=sub)
        sub += 1


def plot_candle_gather(data_frame, last_date, sub):
    columns = 1
    rows = math.ceil(len(data_frame) / columns)

    fig = plt.figure(figsize=(columns * 15, rows * 5 / 2))
    for i in range(len(data_frame)):
        ts_code = data_frame.loc[i, 'ts_code']
        name = data_frame.loc[i, 'name']
        ax = fig.add_subplot(rows, columns, i + 1)
        plot_candle(ax=ax, ts_code=ts_code, name=name, last_date=last_date)

    plt.tight_layout()
    plt.savefig('../../buffer/history_analyze/{date}_history_analyze_{sub}.png'.format(date=last_date, sub=sub))

def plot_candle(ax, ts_code, name, last_date):
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

    plt.title('{ts_code} {name}'.format(ts_code=ts_code, name=name),
              fontproperties='Heiti TC')
    mpf.candlestick2_ochl(ax, df['open'], df['close'], df['high'], df['low'],
                          width=0.5, colorup='red', colordown='green',
                          alpha=0.5)
    # plt.grid()
    print('plot {ts_code} {name}'.format(ts_code=ts_code, name=name))


if __name__ == '__main__':
    main(offset=0)