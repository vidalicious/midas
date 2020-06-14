# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import midas.core.analyzer.api as api

import midas.core.data.models as models
from midas.core.data.engine import main_session
import midas.bin.env as env
import shutil
import os


COL_DAILY_BREAK = 'COL_DAILY_BREAK'
COL_DAILY_AMPLITUDE = 'COL_DAILY_AMPLITUDE'
# COL_NO_LIMIT = 'COL_NO_LIMIT'
COL_LASTPRICE = 'COL_LASTPRICE'
COL_FLOAT_HOLDERS = 'COL_FLOAT_HOLDERS'

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
            data_frame.loc[i, COL_DAILY_BREAK] = api.daily_break(daily, local_scale=60)
            data_frame.loc[i, COL_DAILY_AMPLITUDE] = api.amplitude(daily[:60])

            holders = main_session.query(models.FloatHolderPro).filter(models.FloatHolderPro.ts_code == stock_basic.ts_code).all()
            h_list = []
            for item in holders:
                h_list.append(item.holder_name)
            data_frame.loc[i, COL_FLOAT_HOLDERS] = '\n'.join(h_list)

        except Exception as e:
            print('exception in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### micro amplitude {i} #####'.format(i=i))

    data_frame = data_frame[
                            (data_frame[COL_DAILY_BREAK] == True)
                            & (data_frame[COL_DAILY_AMPLITUDE] < 30)
                           ]

    data_frame = data_frame.sort_values(by=COL_LASTPRICE, ascending=True).reset_index(drop=True)
    # data_frame = data_frame.loc[:, ['ts_code', 'name', 'industry', COL_LASTPRICE, COL_FLOAT_HOLDERS]]

    file_name = '{logs_path}/{date}@Micro_Amplitude.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)

    shutil.rmtree('../../buffer/micro_amplitude/micro_amplitude')
    os.mkdir('../../buffer/micro_amplitude/micro_amplitude')
    for i in range(len(data_frame)):
        ts_code = data_frame.loc[i, 'ts_code']
        name = data_frame.loc[i, 'name']
        plot(ts_code=ts_code, name=name, last_date=LAST_MARKET_DATE, doc='micro_amplitude', file_prefix=i)


def plot(ts_code, name, last_date, doc, file_prefix=0):
    sns.set(style="whitegrid")

    daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == ts_code,
                                                       models.DailyPro.trade_date <= last_date).order_by(
        models.DailyPro.trade_date.desc()).limit(sampling_count).all()

    data = [item.close for item in daily][120::-1]
    data =  pd.DataFrame(data, columns=[ts_code])

    sns.lineplot(data=data, palette="tab10", linewidth=1.5).get_figure().savefig('../../buffer/micro_amplitude/{doc}/{prefix}_{ts_code}_{name}@{date}.png'
        .format(doc=doc, ts_code=ts_code, name=name, date=last_date, prefix=file_prefix))
    plt.clf()
    print('plot {ts_code} {name}'.format(ts_code=ts_code, name=name))


if __name__ == '__main__':
    main(offset=0)