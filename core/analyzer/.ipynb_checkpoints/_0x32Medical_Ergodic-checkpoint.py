# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import midas.core.analyzer.api as api

import midas.core.data.models as models
from midas.core.data.engine import main_session
import midas.bin.env as env
import shutil
import os


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

            holders = main_session.query(models.FloatHolderPro).filter(models.FloatHolderPro.ts_code == stock_basic.ts_code).all()
            h_list = []
            for item in holders:
                h_list.append(item.holder_name)
            data_frame.loc[i, COL_FLOAT_HOLDERS] = '\n'.join(h_list)

        except Exception as e:
            print('exception in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name))
            continue
        print('##### medical ergodic {i} #####'.format(i=i))

    data_frame = data_frame[
                            (data_frame[COL_IS_MEDICAL] == True)
                           ]

    data_frame = data_frame.sort_values(by=COL_LASTPRICE, ascending=True).reset_index(drop=True)
    # data_frame = data_frame.loc[:, ['ts_code', 'name', 'industry', COL_LASTPRICE, COL_FLOAT_HOLDERS]]

    file_name = '{logs_path}/{date}@Medical_Ergodic.csv'.format(date=LAST_MARKET_DATE, logs_path=env.logs_path)
    with open(file_name, 'w', encoding='utf8') as file:
        data_frame.to_csv(file)

    pdf_plot(data_frame=data_frame, last_date=LAST_MARKET_DATE)

    # shutil.rmtree('../../buffer/medical_ergodic/medical_ergodic')
    # os.mkdir('../../buffer/medical_ergodic/medical_ergodic')
    # for i in range(len(data_frame)):
    #     ts_code = data_frame.loc[i, 'ts_code']
    #     name = data_frame.loc[i, 'name']
    #     plot(ts_code=ts_code, name=name, last_date=LAST_MARKET_DATE, doc='medical_ergodic', file_prefix=i)


def plot(ts_code, name, last_date, doc, file_prefix=0):
    sns.set(style="whitegrid")

    daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == ts_code,
                                                       models.DailyPro.trade_date <= last_date).order_by(
        models.DailyPro.trade_date.desc()).limit(sampling_count).all()

    data = [item.close for item in daily][60::-1]
    data =  pd.DataFrame(data, columns=[ts_code])

    sns.lineplot(data=data, palette="tab10", linewidth=1.5).get_figure().savefig('../../buffer/medical_ergodic/{doc}/{prefix}_{ts_code}_{name}@{date}.png'
        .format(doc=doc, ts_code=ts_code, name=name, date=last_date, prefix=file_prefix))
    plt.clf()
    print('plot {ts_code} {name}'.format(ts_code=ts_code, name=name))


def pdf_plot(data_frame, last_date):
    with PdfPages('../../buffer/medical_ergodic/{date}_medical_ergodic.pdf'.format(date=last_date)) as pdf:
        for i in range(len(data_frame))[:10]:
            ts_code = data_frame.loc[i, 'ts_code']
            name = data_frame.loc[i, 'name']
            plot_only(ts_code=ts_code, name=name, last_date=last_date)
            pdf.savefig()
            plt.clf()


def plot_only(ts_code, name, last_date):
    sns.set(style="whitegrid")

    daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == ts_code,
                                                       models.DailyPro.trade_date <= last_date).order_by(
        models.DailyPro.trade_date.desc()).limit(sampling_count).all()

    data = [item.close for item in daily][60::-1]
    data =  pd.DataFrame(data, columns=[ts_code])

    plt.title('')
    sns.lineplot(data=data, palette="tab10", linewidth=1.5)
    # plt.clf()
    print('plot {ts_code} {name}'.format(ts_code=ts_code, name=name))


if __name__ == '__main__':
    main(offset=0)