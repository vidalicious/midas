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
COL_DAILY_BREAK_OFFSET1 = 'COL_DAILY_BREAK_OFFSET1'
COL_IS_MEDICAL = 'COL_IS_MEDICAL'
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

            data_frame.loc[i, COL_IS_MEDICAL] = api.is_medical(stock_basic.industry)

            daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == stock_basic.ts_code,
                                                               models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(
                models.DailyPro.trade_date.desc()).limit(sampling_count).all()
            data_frame.loc[i, COL_LASTPRICE] = daily[0].close
            data_frame.loc[i, COL_DAILY_BREAK] = api.daily_break(daily, local_scale=60)
            data_frame.loc[i, COL_DAILY_BREAK_OFFSET1] = api.daily_break(daily[1:], local_scale=60)

            holders = main_session.query(models.FloatHolderPro).filter(models.FloatHolderPro.ts_code == stock_basic.ts_code).all()
            h_list = []
            for item in holders:
                h_list.append(item.holder_name)
            data_frame.loc[i, COL_FLOAT_HOLDERS] = '\n'.join(h_list)

        except Exception as e:
            print('exception in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### medical break {i} #####'.format(i=i))

    data_frame = data_frame[
                            (data_frame[COL_DAILY_BREAK] == True)
                            & (data_frame[COL_IS_MEDICAL] == True)
                           ]

    data_frame = data_frame.sort_values(by=COL_LASTPRICE, ascending=True).reset_index(drop=True)
    # data_frame = data_frame.loc[:, ['ts_code', 'name', 'industry', COL_LASTPRICE, COL_FLOAT_HOLDERS]]

    file_name = '{logs_path}/{date}@Medical_Break.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)

    shutil.rmtree('../../buffer/medical_break/medical_break')
    os.mkdir('../../buffer/medical_break/medical_break')
    for i in range(len(data_frame)):
        ts_code = data_frame.loc[i, 'ts_code']
        name = data_frame.loc[i, 'name']
        plot(ts_code=ts_code, name=name, last_date=LAST_MARKET_DATE, doc='medical_break', file_prefix=i)

    data_frame = data_frame[
                            (data_frame[COL_DAILY_BREAK_OFFSET1] == False)
                           ]
    data_frame = data_frame.sort_values(by=COL_LASTPRICE, ascending=True).reset_index(drop=True)
    file_name = '{logs_path}/{date}@Medical_Break_differ.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)

    shutil.rmtree('../../buffer/medical_break/medical_break_differ')
    os.mkdir('../../buffer/medical_break/medical_break_differ')
    for i in range(len(data_frame)):
        ts_code = data_frame.loc[i, 'ts_code']
        name = data_frame.loc[i, 'name']
        plot(ts_code=ts_code, name=name, last_date=LAST_MARKET_DATE, doc='medical_break_differ', file_prefix=i)


def plot(ts_code, name, last_date, doc, file_prefix=0):
    sns.set(style="whitegrid")

    daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == ts_code,
                                                       models.DailyPro.trade_date <= last_date).order_by(
        models.DailyPro.trade_date.desc()).limit(sampling_count).all()

    data = [item.close for item in daily][120::-1]
    data =  pd.DataFrame(data, columns=[ts_code])

    sns.lineplot(data=data, palette="tab10", linewidth=1.5).get_figure().savefig('../../buffer/medical_break/{doc}/{prefix}_{ts_code}_{name}@{date}.png'
        .format(doc=doc, ts_code=ts_code, name=name, date=last_date, prefix=file_prefix))
    plt.clf()
    print('plot {ts_code} {name}'.format(ts_code=ts_code, name=name))


if __name__ == '__main__':
    main(offset=0)